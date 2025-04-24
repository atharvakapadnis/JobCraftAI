"""
MCP Server implementation for JobCraftAI

This module implements a Model Context Protocol (MCP) server that exposes
JobCraftAI functionality to MCP clients.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator

from app.config import settings
from app.services.linkedin_generator import LinkedInGenerator
from app.services.cover_letter_generator import CoverLetterGenerator
from app.services.resume_optimizer import ResumeOptimizer
from app.services.resume_parser import ResumeParser

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """
    MCP Server implementation for JobCraftAI
    """
    
    def __init__(self):
        """
        Initialize the MCP server with tools
        """
        self.tools = {
            "linkedin_generator": {
                "name": "linkedin_generator",
                "description": "Generate LinkedIn connection requests and job inquiries",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Target person's name"},
                        "message_type": {"type": "string", "enum": ["connection_request", "job_inquiry"], "description": "Type of message to generate"},
                        "about_section": {"type": "string", "description": "Target person's About section (optional)"},
                        "title": {"type": "string", "description": "Target person's title (optional)"},
                        "company": {"type": "string", "description": "Target person's company (optional)"},
                        "job_title": {"type": "string", "description": "Job title (required for job_inquiry)"},
                        "company_name": {"type": "string", "description": "Company name (required for job_inquiry)"},
                        "job_description": {"type": "string", "description": "Job description (optional for job_inquiry)"}
                    },
                    "required": ["name", "message_type"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "generated_message": {"type": "string"},
                        "character_count": {"type": "integer"}
                    }
                }
            },
            "cover_letter_generator": {
                "name": "cover_letter_generator",
                "description": "Generate personalized cover letters",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resume_data": {"type": "object", "description": "Structured resume data"},
                        "job_description": {"type": "string", "description": "Job description text"},
                        "company_name": {"type": "string", "description": "Company name"},
                        "job_title": {"type": "string", "description": "Job title"},
                        "tone": {"type": "string", "enum": ["professional", "formal", "friendly", "enthusiastic", "confident", "humble"], "description": "Tone of the cover letter"},
                        "emphasized_projects": {"type": "array", "items": {"type": "string"}, "description": "List of projects to emphasize (optional)"},
                        "emphasized_skills": {"type": "array", "items": {"type": "string"}, "description": "List of skills to emphasize (optional)"},
                        "emphasized_experiences": {"type": "array", "items": {"type": "string"}, "description": "List of experiences to emphasize (optional)"},
                        "personal_note": {"type": "string", "description": "Additional context from the user (optional)"},
                        "portfolio_url": {"type": "string", "description": "User's portfolio URL (optional)"}
                    },
                    "required": ["resume_data", "job_description", "company_name", "job_title"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"}
                    }
                }
            },
            "resume_optimizer": {
                "name": "resume_optimizer",
                "description": "Generate optimization suggestions for a resume based on a job description",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resume_data": {"type": "object", "description": "Structured resume data"},
                        "job_description": {"type": "string", "description": "Job description text"}
                    },
                    "required": ["resume_data", "job_description"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "match_score": {"type": "number"},
                        "suggestions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "content": {"type": "string"},
                                    "priority": {"type": "string"}
                                }
                            }
                        },
                        "skill_matches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill_name": {"type": "string"},
                                    "is_present": {"type": "string"},
                                    "importance": {"type": "string"},
                                    "suggestion": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request
        
        Args:
            request: MCP request object
            
        Returns:
            MCP response object
        """
        request_type = request.get("type")
        
        if request_type == "discover":
            return await self.handle_discover()
        elif request_type == "invoke":
            return await self.handle_invoke(request)
        else:
            return {
                "type": "error",
                "error": {
                    "message": f"Unsupported request type: {request_type}"
                }
            }
    
    async def handle_discover(self) -> Dict[str, Any]:
        """
        Handle a discover request
        
        Returns:
            MCP discover response
        """
        return {
            "type": "discover_response",
            "tools": list(self.tools.values())
        }
    
    async def handle_invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an invoke request
        
        Args:
            request: MCP invoke request
            
        Returns:
            MCP invoke response
        """
        tool_name = request.get("tool")
        if tool_name not in self.tools:
            return {
                "type": "error",
                "error": {
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        params = request.get("params", {})
        
        try:
            if tool_name == "linkedin_generator":
                result = await self.invoke_linkedin_generator(params)
            elif tool_name == "cover_letter_generator":
                result = await self.invoke_cover_letter_generator(params)
            elif tool_name == "resume_optimizer":
                result = await self.invoke_resume_optimizer(params)
            else:
                return {
                    "type": "error",
                    "error": {
                        "message": f"Tool implementation not found: {tool_name}"
                    }
                }
            
            return {
                "type": "invoke_response",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {str(e)}")
            return {
                "type": "error",
                "error": {
                    "message": f"Error invoking tool {tool_name}: {str(e)}"
                }
            }
    
    async def invoke_linkedin_generator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the LinkedIn message generator
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool result
        """
        message_type = params.get("message_type")
        name = params.get("name")
        
        if not name:
            raise ValueError("Missing required parameter: name")
        
        if message_type == "connection_request":
            return await LinkedInGenerator.generate_connection_request(
                name=name,
                about_section=params.get("about_section"),
                title=params.get("title"),
                company=params.get("company")
            )
        elif message_type == "job_inquiry":
            job_title = params.get("job_title")
            company_name = params.get("company_name")
            
            if not job_title or not company_name:
                raise ValueError("Job inquiry requires job_title and company_name parameters")
            
            return await LinkedInGenerator.generate_job_inquiry(
                name=name,
                job_title=job_title,
                company_name=company_name,
                about_section=params.get("about_section"),
                title=params.get("title"),
                company=params.get("company"),
                job_description=params.get("job_description")
            )
        else:
            raise ValueError(f"Invalid message_type: {message_type}")
    
    async def invoke_cover_letter_generator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the cover letter generator
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool result
        """
        resume_data = params.get("resume_data")
        job_description = params.get("job_description")
        company_name = params.get("company_name")
        job_title = params.get("job_title")
        
        if not resume_data or not job_description or not company_name or not job_title:
            raise ValueError("Missing required parameters for cover letter generation")
        
        content = await CoverLetterGenerator.generate_cover_letter(
            resume_data=resume_data,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            tone=params.get("tone", "professional"),
            emphasized_projects=params.get("emphasized_projects"),
            emphasized_skills=params.get("emphasized_skills"),
            emphasized_experiences=params.get("emphasized_experiences"),
            personal_note=params.get("personal_note"),
            portfolio_url=params.get("portfolio_url")
        )
        
        return {"content": content}
    
    async def invoke_resume_optimizer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the resume optimizer
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool result
        """
        resume_data = params.get("resume_data")
        job_description = params.get("job_description")
        
        if not resume_data or not job_description:
            raise ValueError("Missing required parameters for resume optimization")
        
        return await ResumeOptimizer.optimize_resume(
            resume_data=resume_data,
            job_description=job_description
        )