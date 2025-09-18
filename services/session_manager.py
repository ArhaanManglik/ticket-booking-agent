"""
Session management module for train booking agent.
Handles conversation state, booking data persistence, and session lifecycle.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from services.ai_extractor import TravelInfo


@dataclass
class ConversationMessage:
    """Represents a single message in the conversation"""
    timestamp: datetime
    sender: str  # 'user' or 'assistant'
    message: str
    message_type: str = 'text'  # 'text', 'selection', 'confirmation'
    metadata: Optional[Dict] = None


@dataclass
class SessionState:
    """Represents the current state of a booking session"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    current_step: str  # 'initial', 'collecting_info', 'searching_trains', 'train_selection', 'booking', 'completed'
    travel_info: TravelInfo
    conversation_history: List[ConversationMessage]
    available_trains: List[Dict] = None
    selected_train: Optional[Dict] = None
    booking_reference: Optional[str] = None
    pending_selections: List[str] = None  # For handling multi-step selections
    context_data: Dict = None  # Additional context for AI processing
    user_preferences: Dict = None  # Learned user preferences


class SessionManager:
    """Manages user sessions and conversation state"""
    
    def __init__(self):
        """Initialize session manager"""
        # In production, this would be replaced with database storage
        self.sessions: Dict[str, SessionState] = {}
        self.max_sessions = 1000  # Limit memory usage
        
    def create_session(self, session_id: str) -> SessionState:
        """
        Create a new session
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            New SessionState object
        """
        now = datetime.now()
        
        session_state = SessionState(
            session_id=session_id,
            created_at=now,
            last_activity=now,
            current_step='initial',
            travel_info=TravelInfo(),
            conversation_history=[],
            available_trains=[],
            selected_train=None,
            booking_reference=None,
            pending_selections=[],
            context_data={},
            user_preferences={}
        )
        
        # Clean up old sessions if needed
        if len(self.sessions) >= self.max_sessions:
            self._cleanup_old_sessions()
            
        self.sessions[session_id] = session_state
        return session_state
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Get existing session or create new one
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionState object or None if not found
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_activity = datetime.now()
            return session
        return None
    
    def get_or_create_session(self, session_id: str) -> SessionState:
        """
        Get existing session or create new one
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionState object
        """
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session
    
    def update_travel_info(self, session_id: str, travel_info: TravelInfo) -> bool:
        """
        Update travel information for a session
        
        Args:
            session_id: Session identifier
            travel_info: Updated travel information
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.travel_info = travel_info
            session.last_activity = datetime.now()
            return True
        return False
    
    def add_conversation_message(self, session_id: str, sender: str, message: str, 
                                message_type: str = 'text', metadata: Dict = None) -> bool:
        """
        Add a message to the conversation history
        
        Args:
            session_id: Session identifier
            sender: 'user' or 'assistant'
            message: Message content
            message_type: Type of message
            metadata: Additional message metadata
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            conversation_message = ConversationMessage(
                timestamp=datetime.now(),
                sender=sender,
                message=message,
                message_type=message_type,
                metadata=metadata or {}
            )
            session.conversation_history.append(conversation_message)
            session.last_activity = datetime.now()
            return True
        return False
    
    def update_session_step(self, session_id: str, new_step: str) -> bool:
        """
        Update the current step of the session
        
        Args:
            session_id: Session identifier
            new_step: New step name
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.current_step = new_step
            session.last_activity = datetime.now()
            return True
        return False
    
    def set_available_trains(self, session_id: str, trains: List[Dict]) -> bool:
        """
        Set available trains for the session
        
        Args:
            session_id: Session identifier
            trains: List of available trains
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.available_trains = trains
            session.last_activity = datetime.now()
            return True
        return False
    
    def set_selected_train(self, session_id: str, train: Dict) -> bool:
        """
        Set the selected train for the session
        
        Args:
            session_id: Session identifier
            train: Selected train data
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.selected_train = train
            session.last_activity = datetime.now()
            return True
        return False
    
    def get_conversation_context(self, session_id: str, last_n_messages: int = 5) -> str:
        """
        Get conversation context for AI processing
        
        Args:
            session_id: Session identifier
            last_n_messages: Number of recent messages to include
            
        Returns:
            Formatted conversation context
        """
        session = self.get_session(session_id)
        if not session:
            return ""
        
        recent_messages = session.conversation_history[-last_n_messages:] if session.conversation_history else []
        
        context_parts = []
        for msg in recent_messages:
            context_parts.append(f"{msg.sender}: {msg.message}")
        
        return "\n".join(context_parts)
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get a summary of the current session state
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session summary
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session.session_id,
            'current_step': session.current_step,
            'travel_info': asdict(session.travel_info),
            'has_available_trains': bool(session.available_trains),
            'has_selected_train': bool(session.selected_train),
            'conversation_length': len(session.conversation_history),
            'last_activity': session.last_activity.isoformat(),
            'created_at': session.created_at.isoformat()
        }
    
    def reset_session(self, session_id: str) -> bool:
        """
        Reset session to initial state
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.create_session(session_id)
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def update_context_data(self, session_id: str, key: str, value: Any) -> bool:
        """
        Update context data for the session
        
        Args:
            session_id: Session identifier
            key: Context key
            value: Context value
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            if session.context_data is None:
                session.context_data = {}
            session.context_data[key] = value
            session.last_activity = datetime.now()
            return True
        return False
    
    def update_user_preferences(self, session_id: str, preferences: Dict) -> bool:
        """
        Update learned user preferences
        
        Args:
            session_id: Session identifier
            preferences: Dictionary of user preferences
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            if session.user_preferences is None:
                session.user_preferences = {}
            session.user_preferences.update(preferences)
            session.last_activity = datetime.now()
            return True
        return False
    
    def is_step_completed(self, session_id: str, step: str) -> bool:
        """
        Check if a particular step has been completed
        
        Args:
            session_id: Session identifier
            step: Step name to check
            
        Returns:
            True if step is completed, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        step_order = ['initial', 'collecting_info', 'searching_trains', 'train_selection', 'booking', 'completed']
        
        try:
            current_index = step_order.index(session.current_step)
            check_index = step_order.index(step)
            return current_index > check_index
        except ValueError:
            return False
    
    def get_missing_information(self, session_id: str) -> List[str]:
        """
        Get list of missing critical information for booking
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of missing information fields
        """
        session = self.get_session(session_id)
        if not session:
            return ['session_not_found']
        
        missing = []
        travel_info = session.travel_info
        
        if not travel_info.source_city:
            missing.append('source_city')
        if not travel_info.destination_city:
            missing.append('destination_city')
        if not travel_info.travel_date:
            missing.append('travel_date')
        if not travel_info.passengers or travel_info.passengers <= 0:
            missing.append('passengers')
            
        return missing
    
    def _cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """
        Clean up old inactive sessions
        
        Args:
            max_age_hours: Maximum age of sessions to keep
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        sessions_to_delete = []
        for session_id, session in self.sessions.items():
            if session.last_activity.timestamp() < cutoff_time:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self.sessions[session_id]
    
    def export_session_data(self, session_id: str) -> Optional[Dict]:
        """
        Export session data for persistence or analysis
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with complete session data
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'current_step': session.current_step,
            'travel_info': asdict(session.travel_info),
            'conversation_history': [
                {
                    'timestamp': msg.timestamp.isoformat(),
                    'sender': msg.sender,
                    'message': msg.message,
                    'message_type': msg.message_type,
                    'metadata': msg.metadata
                }
                for msg in session.conversation_history
            ],
            'available_trains': session.available_trains,
            'selected_train': session.selected_train,
            'booking_reference': session.booking_reference,
            'pending_selections': session.pending_selections,
            'context_data': session.context_data,
            'user_preferences': session.user_preferences
        }
