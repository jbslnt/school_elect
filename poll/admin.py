from django.contrib import admin
from .models import (
    ElectionEvent, Position, Candidate,
    UserVote, ControlVote, UserProfile
)


@admin.register(ElectionEvent)
class ElectionEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'status')
    ordering = ('-start_time',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event')
    list_filter = ('event',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'total_vote', 'partylist')
    list_filter = ('position',)
    search_fields = ('name', 'partylist')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'department', 'program', 'accepted_terms')
    list_filter = ('department', 'program', 'accepted_terms')
    search_fields = ('user__username', 'student_id')
