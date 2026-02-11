import logging

from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    """
    Task to check current overdue loans and send email to the user to return the book.
    """
    current_date = timezone.now()
    pending_loans = Loan.objects.select_related(
        "member", "book", "member__user"
    ).filter(
        is_returned=False,
        due_date__lt=current_date
    )
    if pending_loans.exist():
        logger.info("No pending loaned books!!")
        return

    failed_loan_ids = []
    
    logger.info("Total pending loans: ", pending_loans.count())
    for loan in pending_loans.iterator():
        loan_id = loan.id
        member_email = loan.member.user.email
        book_title = loan.book.title
        
        logger.info(f"Sending mail to {member_email} for {book_title}")
        try:
            send_mail(
                subject='Book Loaned Successfully',
                message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member_email],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(f"Exception raised when sending email to {member_email}: ", e)
            failed_loan_ids.append(loan_id)

    # Retry the failed loans
    for failed_loan_id in failed_loan_ids:
        logger.info(f"Retrying loan id {failed_loan_id}!")
        send_loan_notification.run(failed_loan_id)
