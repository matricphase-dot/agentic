"""
Gemini-powered Planner Agent
"""

import os
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from agents.planner import WorkflowStep, WorkflowPlan, AgentType
import hashlib

logger = logging.getLogger(__name__)

class GeminiPlanner:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def create_workflow_plan(self, task: str) -> WorkflowPlan:
        logger.info(f"🤖 Gemini planning for: {task}")
        
        prompt = f"""You are an expert workflow planner for a multi-agent system.
        
        TASK: {task}

        Available Agents:
        1. PLANNER - Breaks down tasks, creates plans
        2. RESEARCHER - Fetches data from web/APIs (PyPI, websites, databases)
        3. CODER - Writes/executes code, analyzes data, creates scripts
        4. QA - Verifies correctness, runs tests
        5. EXECUTOR - Executes final actions

        Available Tools:
        - pypi_client: Get package info from PyPI
        - web_scraper: Scrape website content
        - sql_executor: Run SQL queries
        - python_executor: Execute Python code
        - http_client: Make HTTP requests
        - file_handler: Read/write files
        - data_analyzer: Analyze datasets

        Create a workflow plan with these steps:
        1. Research phase (gather information)
        2. Analysis/processing phase
        3. Verification phase
        4. Output/execution phase

        Return JSON format:
        {{
            "steps": [
                {{
                    "id": 1,
                    "description": "step description",
                    "agent_type": "PLANNER|RESEARCHER|CODER|QA|EXECUTOR",
                    "tools": ["tool1", "tool2"],
                    "dependencies": [],
                    "expected_output": "what this step produces",
                    "validation_criteria": ["criteria1", "criteria2"]
                }}
            ],
            "estimated_time": 60,
            "required_tools": ["tool1", "tool2"],
            "confidence_score": 0.95
        }}

        Important rules:
        - Maximum 4 steps for simple tasks
        - Each step must be executable by a single agent
        - Include appropriate tools for each step
        - Be realistic about time estimates
        - Include validation criteria

        Provide ONLY the JSON response, no other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON (Gemini sometimes adds markdown)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(response_text)
            
            # Convert to WorkflowPlan object
            steps = []
            for step_data in plan_data["steps"]:
                step = WorkflowStep(
                    id=step_data["id"],
                    description=step_data["description"],
                    agent_type=AgentType(step_data["agent_type"].lower()),
                    tools=step_data.get("tools", []),
                    dependencies=step_data.get("dependencies", []),
                    expected_output=step_data["expected_output"],
                    validation_criteria=step_data.get("validation_criteria", [])
                )
                steps.append(step)
            
            plan_hash = hashlib.md5(task.encode() + response_text.encode()).hexdigest()[:16]
            
            return WorkflowPlan(
                task=task,
                steps=steps,
                estimated_time=plan_data.get("estimated_time", 60),
                required_tools=plan_data.get("required_tools", []),
                confidence_score=plan_data.get("confidence_score", 0.8),
                plan_hash=plan_hash
            )
            
        except Exception as e:
            logger.error(f"Gemini planning failed: {e}")
            raise