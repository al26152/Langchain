"""
agent_hub.py

AGENT COMMUNICATION HUB FOR BIDIRECTIONAL MULTI-AGENT NETWORK

PURPOSE:
  Central message bus and state management for bidirectional agent communication.
  Transforms sequential pipeline into a true agent network where agents can
  request actions from each other.

FEATURES:
  - Agent registration and routing
  - Message queue with priority handling
  - Shared state management (evidence pool, document selection, context)
  - Request/Response/Broadcast message types
  - Comprehensive logging of all agent communications
  - Non-blocking request handling with response tracking

ARCHITECTURE:
  Hub coordinates between agents without forcing sequential execution.
  Agents can send requests, respond to requests, and broadcast information.
  All communications are logged for debugging and analysis.

USAGE:
  from agent_hub import AgentHub

  hub = AgentHub()
  hub.register_agent("evidence", evidence_agent)
  hub.register_agent("critique", critique_agent)

  hub.send_message(
      from_agent="critique",
      to_agent="evidence",
      action="search_targeted",
      params={"gaps": [...], "boost_web": True}
  )

  result = hub.process_queue()
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class Message:
    """Represents a single message in the agent network."""

    def __init__(
        self,
        message_type: str,
        from_agent: str,
        to_agent: Optional[str],
        action: str,
        params: Dict = None,
        priority: int = 0,
        request_id: Optional[str] = None,
    ):
        """
        Initialize a message.

        Args:
            message_type: "REQUEST", "RESPONSE", or "BROADCAST"
            from_agent: Sending agent name
            to_agent: Target agent name (None for broadcasts)
            action: Action to perform
            params: Action parameters
            priority: Higher = executed first (0-10)
            request_id: Links responses to requests
        """
        self.message_type = message_type
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.action = action
        self.params = params or {}
        self.priority = priority
        self.request_id = request_id or f"{from_agent}_{action}_{datetime.now().timestamp()}"
        self.timestamp = datetime.now()
        self.status = "QUEUED"

    def to_dict(self) -> Dict:
        """Convert message to dictionary for logging."""
        return {
            "message_type": self.message_type,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "action": self.action,
            "params_keys": list(self.params.keys()),
            "priority": self.priority,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
        }


class AgentHub:
    """
    Central hub for agent communication and state management.

    Maintains agent registry, message queue, and shared state.
    Enables bidirectional communication between agents.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize AgentHub.

        Args:
            verbose: Enable detailed logging of all communications
        """
        self.agents: Dict[str, Any] = {}
        self.message_queue: List[Message] = []
        self.response_map: Dict[str, Any] = {}
        self.communication_log: List[Dict] = []
        self.verbose = verbose

        # Shared state across all agents
        self.shared_state = {
            "evidence_pool": [],  # Accumulated evidence
            "web_context": {},  # Web lookup results
            "document_selection": [],  # Selected documents
            "iteration_history": [],  # All iteration results
            "critique_history": [],  # All critique results
            "gaps_identified": [],  # All gaps by any agent
            "web_search_invoked": False,  # Track if web search has run
            "last_web_search_iteration": 0,  # When web search last ran
            "document_expansion_count": 0,  # Number of expansions
        }

        self._log(
            "HUB_INITIALIZED",
            {"message": "AgentHub created and ready for agent registration"},
        )

    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """
        Register an agent with the hub.

        Args:
            agent_name: Name to identify agent in communications
            agent_instance: Agent object instance
        """
        self.agents[agent_name] = agent_instance
        self._log("AGENT_REGISTERED", {"agent": agent_name})

    def send_message(
        self,
        from_agent: str,
        to_agent: Optional[str],
        action: str,
        params: Dict = None,
        message_type: str = "REQUEST",
        priority: int = 0,
    ) -> str:
        """
        Send a message between agents.

        Args:
            from_agent: Sending agent name
            to_agent: Target agent name (None for broadcasts)
            action: Action name
            params: Action parameters
            message_type: "REQUEST", "RESPONSE", or "BROADCAST"
            priority: 0-10, higher executes first

        Returns:
            request_id for tracking
        """
        msg = Message(
            message_type=message_type,
            from_agent=from_agent,
            to_agent=to_agent,
            action=action,
            params=params,
            priority=priority,
        )

        self.message_queue.append(msg)

        # Sort by priority (higher first)
        self.message_queue.sort(key=lambda m: m.priority, reverse=True)

        self._log(
            "MESSAGE_SENT",
            {
                "from": from_agent,
                "to": to_agent,
                "action": action,
                "type": message_type,
                "priority": priority,
                "request_id": msg.request_id,
            },
        )

        return msg.request_id

    def process_queue(self) -> Dict[str, Any]:
        """
        Process all messages in the queue sequentially.

        Returns:
            Dict with results of all processed messages
        """
        results = {"processed": 0, "successful": 0, "failed": 0, "responses": {}}

        while self.message_queue:
            msg = self.message_queue.pop(0)
            msg.status = "PROCESSING"

            try:
                result = self._execute_message(msg)
                msg.status = "COMPLETE"
                results["successful"] += 1

                # Store response if applicable
                if msg.request_id:
                    self.response_map[msg.request_id] = result
                    results["responses"][msg.request_id] = result

            except Exception as e:
                msg.status = "FAILED"
                results["failed"] += 1
                self._log(
                    "MESSAGE_FAILED",
                    {
                        "from": msg.from_agent,
                        "to": msg.to_agent,
                        "action": msg.action,
                        "error": str(e),
                        "request_id": msg.request_id,
                    },
                )

            results["processed"] += 1
            self.communication_log.append(msg.to_dict())

        return results

    def _execute_message(self, msg: Message) -> Any:
        """
        Execute a single message.

        Args:
            msg: Message to execute

        Returns:
            Result from agent's handle_request method
        """
        if msg.message_type == "BROADCAST":
            # Broadcast to all agents
            results = {}
            for agent_name, agent in self.agents.items():
                if agent_name != msg.from_agent:
                    if hasattr(agent, "handle_request"):
                        result = agent.handle_request(msg.action, msg.params)
                        results[agent_name] = result

            self._log(
                "BROADCAST_PROCESSED",
                {
                    "from": msg.from_agent,
                    "action": msg.action,
                    "agents_notified": len(results),
                },
            )
            return results

        else:  # REQUEST or RESPONSE
            target_agent = self.agents.get(msg.to_agent)
            if not target_agent:
                raise ValueError(f"Target agent '{msg.to_agent}' not registered")

            if not hasattr(target_agent, "handle_request"):
                raise ValueError(
                    f"Agent '{msg.to_agent}' does not support handle_request()"
                )

            result = target_agent.handle_request(msg.action, msg.params)

            self._log(
                "MESSAGE_EXECUTED",
                {
                    "from": msg.from_agent,
                    "to": msg.to_agent,
                    "action": msg.action,
                    "request_id": msg.request_id,
                },
            )

            return result

    def get_shared_state(self, key: str = None) -> Any:
        """
        Get shared state value(s).

        Args:
            key: Specific state key (None returns all)

        Returns:
            State value or entire state dict
        """
        if key:
            return self.shared_state.get(key)
        return self.shared_state

    def update_shared_state(self, updates: Dict) -> None:
        """
        Update shared state with new values.

        Args:
            updates: Dict of state keys/values to update
        """
        for key, value in updates.items():
            if key in self.shared_state:
                self.shared_state[key] = value
            else:
                raise KeyError(f"Unknown shared state key: {key}")

        self._log(
            "STATE_UPDATED",
            {"keys_updated": list(updates.keys())},
        )

    def append_to_state(self, key: str, item: Any) -> None:
        """
        Append an item to a list in shared state.

        Args:
            key: State key (must be a list)
            item: Item to append
        """
        if key not in self.shared_state:
            raise KeyError(f"Unknown shared state key: {key}")

        if not isinstance(self.shared_state[key], list):
            raise TypeError(f"State key '{key}' is not a list")

        self.shared_state[key].append(item)

    def get_agent(self, agent_name: str) -> Any:
        """
        Get an agent instance by name.

        Args:
            agent_name: Agent name

        Returns:
            Agent instance
        """
        return self.agents.get(agent_name)

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.agents.keys())

    def get_communication_log(self) -> List[Dict]:
        """Get full communication log."""
        return self.communication_log

    def get_communication_summary(self) -> Dict:
        """
        Get summary statistics about communications.

        Returns:
            Dict with communication statistics
        """
        agents_communicating = set()
        actions_used = defaultdict(int)
        message_types = defaultdict(int)

        for msg_dict in self.communication_log:
            agents_communicating.add(msg_dict["from_agent"])
            if msg_dict["to_agent"]:
                agents_communicating.add(msg_dict["to_agent"])

            actions_used[msg_dict["action"]] += 1
            message_types[msg_dict["message_type"]] += 1

        return {
            "total_messages": len(self.communication_log),
            "unique_agents": len(agents_communicating),
            "agents_communicating": list(agents_communicating),
            "actions_used": dict(actions_used),
            "message_types": dict(message_types),
            "successful_messages": sum(
                1 for msg in self.communication_log if msg["status"] == "COMPLETE"
            ),
        }

    def _log(self, event_type: str, details: Dict) -> None:
        """
        Internal logging function.

        Args:
            event_type: Type of event to log
            details: Event details
        """
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{event_type}] {json.dumps(details, indent=2)}")

    def clear_queue(self) -> None:
        """Clear all pending messages from queue."""
        cleared = len(self.message_queue)
        self.message_queue = []
        self._log("QUEUE_CLEARED", {"messages_cleared": cleared})

    def reset_communication_log(self) -> None:
        """Reset communication log (for fresh start)."""
        self.communication_log = []
        self._log("LOG_RESET", {"message": "Communication log cleared"})

    def get_messages_for_agent(self, agent_name: str) -> List[Message]:
        """
        Get all pending messages for a specific agent.

        Args:
            agent_name: Agent name

        Returns:
            List of pending messages for that agent
        """
        return [msg for msg in self.message_queue if msg.to_agent == agent_name]

    def get_agent_communication_history(self, agent_name: str) -> List[Dict]:
        """
        Get all communications involving a specific agent.

        Args:
            agent_name: Agent name

        Returns:
            List of messages involving that agent
        """
        return [
            msg
            for msg in self.communication_log
            if msg["from_agent"] == agent_name or msg["to_agent"] == agent_name
        ]
