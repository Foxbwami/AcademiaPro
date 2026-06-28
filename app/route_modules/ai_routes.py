"""
AI Routes for AcademiaPro
Handles all AI-related endpoints for chat, content generation, and admin features
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services import get_grok_service, get_system_prompt
from app.models import AIConversationMessage
from app.extensions import db
from sqlalchemy import desc
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """
    Chat with AI support
    Requires: message (user message)
    Optional: conversation_id (for multi-turn chat)
    """
    data = request.get_json(silent=True) or {}
    message = data.get('message')
    
    if not message or len(message.strip()) < 1:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        grok = get_grok_service()
        system_prompt = get_system_prompt('chat_support')
        
        messages = [{'role': 'user', 'content': message}]
        history = AIConversationMessage.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(AIConversationMessage.created_at)).limit(10).all()

        for msg in reversed(history):
            messages.insert(0, {'role': msg.role, 'content': msg.content})
        
        response = grok.chat_message(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=int(current_app.config.get('GROQ_MAX_TOKENS', 6000))
        )
        
        if response['success']:
            user_row = AIConversationMessage(
                user_id=current_user.id,
                role='user',
                content=message,
            )
            assistant_row = AIConversationMessage(
                user_id=current_user.id,
                role='assistant',
                content=response['content'],
            )
            db.session.add(user_row)
            db.session.add(assistant_row)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'response': response['content'],
                'conversation_id': assistant_row.id
            })
        else:
            current_app.logger.error(f"AI chat service error: {response.get('error')}")
            return jsonify({
                'success': False,
                'error': 'AI service temporarily unavailable. Please try again in a moment.'
            }), 503
    
    except Exception as e:
        current_app.logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'AI service temporarily unavailable. Please try again in a moment.'
        }), 503


@ai_bp.route('/order-assistance', methods=['POST'])
@login_required
def order_assistance():
    """
    Get AI assistance with order management
    Requires: order_details (dict with order information)
    """
    data = request.get_json(silent=True) or {}
    order_details = data.get('order_details')
    question = data.get('question')
    
    if not order_details or not question:
        return jsonify({'error': 'Order details and question required'}), 400
    
    try:
        grok = get_grok_service()
        system_prompt = get_system_prompt('order_assistance')
        
        prompt = f"""Order Details:
{json.dumps(order_details, indent=2)}

User Question: {question}

Please provide relevant assistance based on the order details."""
        
        response = grok.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=int(current_app.config.get('GROQ_MAX_TOKENS', 6000))
        )
        
        if response['success']:
            return jsonify({
                'success': True,
                'assistance': response['content']
            })
        else:
            return jsonify({
                'success': False,
                'error': response['error']
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Order assistance error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to provide assistance'
        }), 500


@ai_bp.route('/admin/system-analysis', methods=['POST'])
@login_required
def admin_system_analysis():
    """
    Admin endpoint: Analyze system performance
    Requires: admin role
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json(silent=True) or {}
    metrics = data.get('metrics', {})
    
    try:
        grok = get_grok_service()
        response = grok.analyze_system_performance(metrics)
        
        if response['success']:
            return jsonify({
                'success': True,
                'analysis': response['content']
            })
        else:
            return jsonify({
                'success': False,
                'error': response['error']
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"System analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze system'
        }), 500


@ai_bp.route('/admin/content-review', methods=['POST'])
@login_required
def admin_content_review():
    """
    Admin endpoint: Review content for compliance
    Requires: admin role, content (text to review)
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json(silent=True) or {}
    content = data.get('content')
    content_type = data.get('type', 'general')
    
    if not content:
        return jsonify({'error': 'Content required for review'}), 400
    
    try:
        grok = get_grok_service()
        system_prompt = get_system_prompt('admin_content_review')
        
        prompt = f"""Review this {content_type} content for quality and compliance:

{content}

Provide:
1. Quality assessment
2. Compliance issues (if any)
3. Plagiarism concerns (if any)
4. Recommendations"""
        
        response = grok.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=int(current_app.config.get('GROQ_MAX_TOKENS', 6000))
        )
        
        if response['success']:
            return jsonify({
                'success': True,
                'review': response['content']
            })
        else:
            return jsonify({
                'success': False,
                'error': response['error']
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Content review error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to review content'
        }), 500


@ai_bp.route('/admin/dispute-resolution', methods=['POST'])
@login_required
def admin_dispute_resolution():
    """
    Admin endpoint: Get AI assistance with dispute resolution
    Requires: admin role, dispute_details (dict with dispute info)
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json(silent=True) or {}
    dispute_details = data.get('dispute_details')
    
    if not dispute_details:
        return jsonify({'error': 'Dispute details required'}), 400
    
    try:
        grok = get_grok_service()
        system_prompt = get_system_prompt('dispute_resolution')
        
        prompt = f"""Please analyze and help resolve this dispute:

{json.dumps(dispute_details, indent=2)}

Provide:
1. Summary of the conflict
2. Both parties' perspectives
3. Fair assessment
4. Recommended resolution"""
        
        response = grok.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=int(current_app.config.get('GROQ_MAX_TOKENS', 6000))
        )
        
        if response['success']:
            return jsonify({
                'success': True,
                'resolution': response['content']
            })
        else:
            return jsonify({
                'success': False,
                'error': response['error']
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Dispute resolution error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process dispute'
        }), 500


@ai_bp.route('/conversation-history', methods=['GET'])
@login_required
def get_conversation_history():
    """Get user's AI conversation history"""
    try:
        conversations = AIConversationMessage.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(AIConversationMessage.created_at)).limit(50).all()
        
        history = [{
            'id': c.id,
            'role': c.role,
            'content': c.content,
            'created_at': c.created_at.isoformat()
        } for c in conversations]
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        current_app.logger.error(f"Conversation history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve history'
        }), 500
