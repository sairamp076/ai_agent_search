from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Interaction
from .agents.ai_agent import create_ai_agent

@receiver(post_save, sender=Interaction)
def auto_tag_interaction(sender, instance, created, **kwargs):
    """
    Auto-tagging mechanism triggered on interaction save.
    """
    if not created:
        return

    conversation = f"User: {instance.user_query}\nAI: {instance.ai_response}"
    prompt = (
        "Based on the following conversation, suggest relevant tags "
        "(e.g. AI, Coding, History, News).\n\n"
        f"{conversation}\n\nSuggested Tags:"
    )

    try:
        agent = create_ai_agent()
        result = agent({"input": prompt})
        tags = result.get("output", "").split(",")
        tags = [tag.strip() for tag in tags if tag.strip()]

        instance.tags = tags
        instance.save()

    except Exception as e:
        print(f"Error auto-tagging interaction: {e}")
