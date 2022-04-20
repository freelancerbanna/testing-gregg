# from django.dispatch import receiver
#
# from leads.models import Program
# from revenues.models import Segment
# from .tasks import refresh_and_map_programs

# todo Either we remove inactive segments and programs from existing mappings or we ignore it
# choosing to ignore for now as I don't think there is any impact.

# @receiver(post_save, sender=Segment, dispatch_uid='sf_segment_post_save_handler')
# def sf_segment_post_save_handler(sender, instance, *args, **kwargs):
#     """
#     Salesforce mappings need to be reset after segments are removed or deleted.
#     """
#     if 'is_active' in instance.get_dirty_fields():
#         if hasattr(instance.revenue_plan, 'salesforcerevenueplan'):
#             refresh_and_map_programs.delay(instance.revenue_plan.salesforcerevenueplan.id)
#
#
# @receiver(post_save, sender=Program, dispatch_uid='sf_program_post_save_handler')
# def sf_program_post_save_handler(sender, instance, *args, **kwargs):
#     """
#     Salesforce mappings need to be reset after programs are removed or deleted.
#     """
#     if 'is_active' in instance.get_dirty_fields():
#         if hasattr(instance.revenue_plan, 'salesforcerevenueplan'):
#             refresh_and_map_programs.delay(instance.revenue_plan.salesforcerevenueplan.id)
#
# from django.dispatch import receiver
