from django.db import models
from django.forms import ValidationError
from sso.models import User
from django.core.validators import RegexValidator


validate_singapore_phone_number = RegexValidator(
    regex=r'^[689]\d{7}$',
    message='Singapore phone number required (8 digits, without the +65)'
)

validate_date_format = RegexValidator(
    regex=r'^(0[1-9]|1[0-2])/\d{4}$',
    message="Invalid date format. Date must be MM/YYYY format"
)

class Location(models.Model):
    location_name = models.CharField(max_length=50)

    def __str__(self):
        return f"<(ID: {self.id}) {self.location_name}>"

class Locker(models.Model):
    name = models.CharField(max_length=10)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    passcode = models.CharField(max_length=10, default='')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"<(ID: {self.id}) {self.location.location_name} #{self.name}>"

class Booking(models.Model): 
    class AllocationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        WITHDRAWN = "withdrawn", "Withdrawn"
        REJECTED = "rejected", "Rejected"
        AWAITING_PAYMENT = "approved - awaiting payment", "Approved - Awaiting Payment"
        AWAITING_VERIFICATION = "approved - awaiting verification", "Approved - Awaiting Verification"
        ALLOCATED = "allocated", "Allocated"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=50)
    matric_no = models.CharField(max_length=9)
    phone_no = models.CharField(max_length=8, validators=[validate_singapore_phone_number])
    organization_name = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=AllocationStatus.choices, default=AllocationStatus.PENDING)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_month = models.CharField(max_length=7, validators=[validate_date_format])
    duration = models.IntegerField()
    comment = models.CharField(max_length=300, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default='unpaid')
    command = models.CharField(max_length=50, default='')
    end_month = models.CharField(max_length=7, default='')

    def __str__(self):
        return f"<{self.applicant_name} -> {self.locker} ({self.start_month} - {self.duration} month(s))>"

class ULockerAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_send_creation_email = models.BooleanField(default=True)
    is_send_verification_email = models.BooleanField(default=True)
    is_send_allocation_email = models.BooleanField(default=True)
    
    def __str__(self):
        return f'<ULocker Admin: {self.user.username}>'
    
    class Meta:
        verbose_name = 'ULocker Admin'
        verbose_name_plural = 'ULocker Admins'

class ULockerConfig(models.Model):
    monthly_price = models.CharField(max_length=20)
    semesterly_price = models.CharField(max_length=20)
    yearly_price = models.CharField(max_length=20)
    qr_code_image = models.ImageField(upload_to='ulocker/qrcodes/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk and ULockerConfig.objects.exists():
            raise ValidationError('There can only be one ULockerConfig instance')
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return 'ULocker Configurations'
    
    class Meta:
        verbose_name = 'ULocker Config'
        verbose_name_plural = 'ULocker Config'
