import os
from typing import TypedDict, List, Annotated, Dict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from app.config import settings

# --- State Definition ---
class AgentState(TypedDict):
    """The state of our marketing automation graph."""
    incoming_email: str
    sender_name: str
    sender_email: str
    subject: str
    intent: str  # interest, question, unsubscribe, spam
    reply_body: str
    actions_taken: List[str]
    status: str
    instruction: Annotated[str, "optional"]

# --- AI Service Class ---
class AIService:
    def __init__(self):
        self.llm = ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            temperature=0
        )
        self.graph = self._build_auto_reply_graph()

    def _build_auto_reply_graph(self):
        """Constructs the LangGraph for auto-replies."""
        builder = StateGraph(AgentState)

        # 1. Categorization Node
        async def categorize_node(state: AgentState):
            prompt = f"""Analyze this email from {state['sender_name']}:
            
            Subject: {state['subject']}
            Body: {state['incoming_email']}
            
            Categorize the intent into exactly one of these: [interest, question, unsubscribe, spam]
            Return ONLY the category name. No other text, formatting, or labels."""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            category = response.content.strip().lower()
            return {"intent": category}

        # 2. Generator Node
        async def generate_reply_node(state: AgentState):
            if state["intent"] in ["interest", "question"]:
                instruction = state.get("instruction", "")
                system_prompt = f"You are a professional marketer replying to {state['sender_name']}. Keep it concise and warm. Provide the reply in PLAIN TEXT ONLY. Do NOT use HTML, Markdown, or any code tags."
                if instruction:
                    system_prompt += f" MANDATORY INSTRUCTION: {instruction}"
                
                user_prompt = f"Generate a helpful plain-text reply to this: {state['incoming_email']}"
                
                response = await self.llm.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ])
                return {"reply_body": self._clean_text(response.content)}
            elif state["intent"] == "unsubscribe":
                return {"reply_body": "You have been successfully unsubscribed from our list."}
            return {"reply_body": ""}

        # Define Edges and Nodes
        builder.add_node("categorize", categorize_node)
        builder.add_node("generate_reply", generate_reply_node)
        
        builder.set_entry_point("categorize")
        builder.add_edge("categorize", "generate_reply")
        builder.add_edge("generate_reply", END)
        
        return builder.compile()

    def _clean_text(self, text) -> str:
        """Strips markdown code blocks and handles non-string AI responses safely."""
        if not text:
            return ""
            
        # Handle list-based content (some versions of LangChain/Anthropic return blocks)
        if isinstance(text, list):
            text = "".join([t.get("text", "") if isinstance(t, dict) else str(t) for t in text])
        
        text = str(text).strip()
        
        if text.startswith("```"):
            # Remove opening block
            text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
            # Remove closing block
            if text.endswith("```"):
                text = text[:-3]
        return text.strip()

    async def generate_email_content(self, prompt: str) -> str:
        """Standard campaign email generation using ChatAnthropic."""
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a professional email marketer. Generate high-converting email content. IMPORTANT: Output ONLY the plain text of the email. Do NOT include HTML tags, Markdown styling, or any code wrappers."),
                HumanMessage(content=f"Create a plain-text email based on this prompt: {prompt}")
            ])
            return self._clean_text(response.content)
        except Exception as e:
            error_msg = f"AI Error: {str(e)}"
            print(f"Error generating email content: {error_msg}")
            return f"Failed to generate content. {error_msg}"

    async def generate_follow_up_content(self, original_subject: str, original_body: str) -> str:
        """Generates a warm, context-aware follow-up email when a lead has not replied."""
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a professional email marketer. Write a concise, polite follow-up to a previous email you sent. Do NOT invent facts. Keep a consistent marketing tone. Provide ONLY the plain text body (no subject line or HTML). Keep it under 4 sentences."),
                HumanMessage(content=f"Original Subject: {original_subject}\nOriginal Body: {original_body}\n\nPlease generate a follow-up email.")
            ])
            return self._clean_text(response.content)
        except Exception as e:
            print(f"Error generating follow up content: {e}")
            return f"Hi, I just wanted to quickly follow up on my previous email regarding '{original_subject}'. Let me know if you have any questions or would like to chat!"

    async def generate_response_suggestions(self, campaign_subject: str, campaign_body: str) -> List[str]:
        """Generates 3 suggestions for how to handle auto-replies based on campaign content."""
        prompt = f"Based on this email campaign, suggest 3 short, distinct strategies for an AI auto-responder (e.g., 'Be helpful but don't book meetings', 'Focus on pricing objections', 'Push for a 5-min discovery call').\n\nSubject: {campaign_subject}\nBody: {campaign_body}\n\nReturn EXACTLY 3 bullet points, each on a new line, no other text."
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            lines = self._clean_text(response.content).strip().split("\n")
            return [l.strip("- ").strip("123. ").strip() for l in lines if l.strip()][:3]
        except:
            return ["Be professional and helpful", "Try to book a short call", "Answer basic questions about the product"]

    async def process_with_graph(self, email_data: Dict) -> Dict:
        """Invokes the LangGraph for a single incoming email."""
        initial_state: AgentState = {
            "incoming_email": email_data["body"],
            "sender_name": email_data["name"],
            "sender_email": email_data["email"],
            "subject": email_data["subject"],
            "intent": "",
            "reply_body": "",
            "actions_taken": [],
            "status": "pending"
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state

ai_service = AIService()
