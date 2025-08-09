# app/langflow_runner.py
import requests
import json
import uuid
from typing import Dict, Optional
import os

class LangFlowRunner:
    def __init__(self):
        self.base_url = os.getenv("LANGFLOW_HOST", "http://localhost:7860")
        self.flow_id = os.getenv("LANGFLOW_FLOW_ID")
        self.api_key = os.getenv("LANGFLOW_API_KEY")
        
        if not self.api_key:
            raise Exception("LANGFLOW_API_KEY environment variable is required")
        
    async def run_flow(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Use the EXACT format from LangFlow API
        payload = {
            "output_type": "chat",
            "input_type": "chat", 
            "input_value": message
        }
        
        # Include the API key header
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        try:
            print(f"🔗 Calling: {self.base_url}/api/v1/run/{self.flow_id}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/run/{self.flow_id}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"📡 Status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            # Debug: Print the raw response structure
            print(f"📄 Raw Response Keys: {list(result.keys())}")
            
            # Extract the clean response and determine agent type
            agent_response, agent_type = self._extract_best_response(result, message)
            
            print(f"✅ Response from {agent_type} agent: {agent_response[:100]}...")
            
            return {
                "response": agent_response,
                "agent_type": agent_type,
                "conversation_id": conversation_id,
                "confidence": "high"
            }
            
        except Exception as e:
            print(f"❌ LangFlow execution error: {str(e)}")
            raise Exception(f"LangFlow execution error: {str(e)}")

    def _extract_best_response(self, result: Dict, original_message: str) -> tuple[str, str]:
        """Extract the best response from the multi-agent system"""
        try:
            agent_responses = []
            
            # Navigate the correct JSON structure
            if "outputs" in result:
                for output in result["outputs"]:
                    # The structure is: outputs -> results -> message
                    if "results" in output and "message" in output["results"]:
                        message_data = output["results"]["message"]
                        
                        # Extract response text
                        response_text = message_data.get("text", "")
                        
                        # Extract agent information from properties
                        properties = message_data.get("properties", {})
                        source = properties.get("source", {})
                        agent_id = source.get("id", "Unknown")
                        
                        if response_text and response_text.strip():
                            agent_responses.append({
                                "text": response_text,
                                "agent_id": agent_id,
                                "length": len(response_text),
                                "is_detailed": len(response_text) > 200  # Consider detailed if >200 chars
                            })
                            
                            print(f"📝 Found response from {agent_id}: {response_text[:100]}...")
            
            if not agent_responses:
                print("❌ No valid responses found in result")
                return "I apologise, but I couldn't process your request.", "general"
            
            # Determine the best response based on message content and response quality
            best_response = self._select_best_response(agent_responses, original_message)
            agent_type = self._determine_agent_type(best_response["agent_id"], best_response["text"], original_message)
            
            print(f"🎯 Selected {agent_type} agent ({best_response['agent_id']}): {len(best_response['text'])} chars")
            
            return best_response["text"], agent_type
            
        except Exception as e:
            print(f"❌ Error extracting response: {e}")
            return "Error processing response", "general"

    def _select_best_response(self, responses: list, original_message: str) -> dict:
        """Select the most appropriate response based on content and context"""
        
        # Classify the original message
        message_lower = original_message.lower()
        
        # Technical issue keywords
        technical_keywords = ['troubleshoot', 'error', 'problem', 'issue', 'setup', 'install', 
                            'fix', 'broken', 'not working', "won't", "can't", 'turn on', 'boot',
                            'crash', 'freeze', 'malfunction', 'repair']
        
        # Product inquiry keywords  
        product_keywords = ['product', 'price', 'cost', 'laptop', 'computer', 'specs', 
                          'features', 'model', 'recommend', 'buy', 'purchase', 'compare']
        
        # General/policy keywords
        general_keywords = ['return', 'refund', 'exchange', 'warranty', 'shipping', 
                          'delivery', 'order', 'payment', 'policy', 'account']
        
        is_technical = any(keyword in message_lower for keyword in technical_keywords)
        is_product = any(keyword in message_lower for keyword in product_keywords)
        is_general = any(keyword in message_lower for keyword in general_keywords)
        
        print(f"🔍 Message analysis - Technical: {is_technical}, Product: {is_product}, General: {is_general}")
        
        # Score each response
        scored_responses = []
        for response in responses:
            score = 0
            agent_id = response["agent_id"]
            text = response["text"].lower()
            
            # Agent type identification
            is_technical_agent = "TGW0N" in agent_id or "technical" in agent_id.lower()
            is_product_agent = "VjuOy" in agent_id or "product" in agent_id.lower()  
            is_general_agent = "Vkvkg" in agent_id or "general" in agent_id.lower()
            
            # Match agent specialisation with query type
            if is_technical and is_technical_agent:
                score += 50
            elif is_product and is_product_agent:
                score += 50  
            elif is_general and is_general_agent:
                score += 50
            
            # Prefer detailed, actionable responses
            if response["length"] > 500:  # Long, detailed response
                score += 30
            elif response["length"] > 200:  # Medium response
                score += 15
                
            # Look for actionable content in technical responses
            if is_technical and any(word in text for word in ['steps', 'check', 'try', 'follow', 'press', 'connect']):
                score += 25
                
            # Avoid redirect responses (agents saying "contact other team")
            if any(phrase in text for phrase in ['technical support team', 'product specialist', 'general support']):
                score -= 20
                
            scored_responses.append({
                **response,
                "score": score,
                "agent_type": "technical" if is_technical_agent else "product" if is_product_agent else "general"
            })
            
            print(f"📊 {agent_id} ({response['agent_type']}): {score} points, {response['length']} chars")
        
        # Return the highest scoring response
        best = max(scored_responses, key=lambda x: x["score"])
        print(f"🏆 Winner: {best['agent_id']} with {best['score']} points")
        
        return best

    def _determine_agent_type(self, agent_id: str, response_text: str, original_message: str) -> str:
        """Determine the agent type from ID and response content"""
        
        # Primary: Agent ID mapping
        if "TGW0N" in agent_id:
            return "technical"
        elif "VjuOy" in agent_id:
            return "product"
        elif "Vkvkg" in agent_id:
            return "general"
            
        # Fallback: Content analysis
        text_lower = response_text.lower()
        
        if any(word in text_lower for word in ['troubleshoot', 'steps', 'check', 'install', 'fix', 'repair']):
            return "technical"
        elif any(word in text_lower for word in ['product', 'specs', 'features', 'model', 'price']):
            return "product"
        else:
            return "general"