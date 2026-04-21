from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model

# Create your models here.
class UserFile(models.Model):
    # Link to the user who uploaded the file
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')

    # Name of the file (e.g., "example.pdf")
    file_name = models.CharField(max_length=255)

    # Path to the file in the media folder (e.g., "uploads/1_20231025_143000_example.pdf")
    file_path = models.CharField(max_length=255)

    # Timestamp of when the file was uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Optional: Store the extracted text (if needed)
    extracted_text = models.TextField(blank=True, null=True)
    summarized_text = models.TextField(blank=True, null=True)
    section = models.CharField(max_length=64, default="full_paper", blank=True)

    def __str__(self):
        """String representation of the model."""
        return f"{self.user.username} - {self.file_name} (Uploaded at: {self.uploaded_at})"

    class Meta:
        # Order files by upload time (newest first)
        ordering = ['-uploaded_at']


