from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import (
    ElectionEvent, Position, Candidate,
    UserVote, ControlVote, UserProfile
)


@admin.register(ElectionEvent)
class ElectionEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'status')
    ordering = ('-start_time',)
    actions = ['generate_pdf_summary']

    def generate_pdf_summary(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one election event.", level='error')
            return

        event = queryset.first()
        positions = Position.objects.filter(event=event).prefetch_related('candidate_set')
        
        # Create the PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="summary_{event.title}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, f"Election Summary Report")
        y -= 25
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Event: {event.title}")
        y -= 20
        p.drawString(50, y, f"Date Range: {event.start_time.strftime('%Y-%m-%d')} to {event.end_time.strftime('%Y-%m-%d')}")
        y -= 30

        for position in positions:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, f"Position: {position.title}")
            y -= 20

            candidates = Candidate.objects.filter(position=position).order_by('-total_vote')
            for candidate in candidates:
                p.setFont("Helvetica", 11)
                line = f"• {candidate.name} ({candidate.partylist or 'No Party'}) - {candidate.total_vote} vote(s)"
                p.drawString(70, y, line)
                y -= 15

                # Get the users who voted for this candidate
                voters = UserVote.objects.filter(candidate=candidate).select_related('user').order_by('user__username')
                if voters.exists():
                    p.setFont("Helvetica-Oblique", 10)
                    for vote in voters:
                        voter_line = f"    - {vote.user.username} at {vote.timestamp.strftime('%Y-%m-%d %H:%M')}"
                        p.drawString(90, y, voter_line)
                        y -= 12
                        if y < 100:
                            p.showPage()
                            y = height - 50
                else:
                    p.setFont("Helvetica-Oblique", 10)
                    p.drawString(90, y, "    No votes.")
                    y -= 12

                y -= 5

            y -= 10
        p.showPage()
        p.save()
        return response

    generate_pdf_summary.short_description = "📄 Generate PDF summary report"

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


@admin.register(UserVote)
class UserVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'candidate', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'candidate__name')