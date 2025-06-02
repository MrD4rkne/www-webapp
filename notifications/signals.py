from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
import logging
from .views import add_event

logger = logging.getLogger(__name__)

@receiver(post_save, sender='boards.GameBoard')
def handle_new_gameboard(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when a new GameBoard is created
    """
    if created:
        try:
            # Only trigger for new boards, not updates
            data = {
                "board_id": str(instance.id),
                "board_name": instance.name,
                "creator_username": instance.user.username
            }
            event = add_event("newBoard", data)
            logger.info(f"SSE event generated for new board: {event}")
        except Exception as e:
            logger.error(f"Error generating SSE event for new board: {e}")


@receiver(post_save, sender='boards.Solution')
def handle_new_solution(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when a new Solution (Path) is created
    """
    if created:
        try:
            # Only trigger for new solutions, not updates
            data = {
                "path_id": str(instance.id),
                "board_id": str(instance.game_board.id),
                "board_name": instance.game_board.name,
                "user_username": instance.user.username
            }
            event = add_event("newPath", data)
            logger.info(f"SSE event generated for new path: {event}")
        except Exception as e:
            logger.error(f"Error generating SSE event for new path: {e}")
