import smtplib
import ssl
from email.message import EmailMessage
import mimetypes
import os


class EmailExporter:
    """
    Envía informes (PDF, PNG, etc.) por correo electrónico.
    Compatible con cualquier servidor SMTP.
    """

    @staticmethod
    def send_email(
        sender_email: str,
        sender_password: str,
        receiver_email: str,
        subject: str,
        body: str,
        attachments: list,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 465
    ):
        """
        Envía un correo con adjuntos.

        attachments = ["ruta1.pdf", "ruta2.png"]
        """

        # Crear mensaje
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Adjuntar archivos
        for file_path in attachments:
            if not os.path.exists(file_path):
                print(f"[WARN] Archivo no encontrado: {file_path}")
                continue

            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type, mime_subtype = mime_type.split("/")

            with open(file_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype=mime_type,
                    subtype=mime_subtype,
                    filename=os.path.basename(file_path)
                )

        # Envío seguro SSL
        context = ssl.create_default_context()

        print("Enviando correo...")

        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Correo enviado correctamente.")
