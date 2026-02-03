from odoo import models, fields, api
from odoo.exceptions import UserError

class EmailSender(models.Model):
    _name = 'email_sender'
    _description = 'Gửi Email'
    _order = 'sent_date desc'

    recipient_ids = fields.Many2many('thong_tin_khach_hang', string="Người nhận", required=True)
    recipient_emails = fields.Char(string="Emails", compute="_compute_recipient_emails", store=True)
    subject = fields.Char(string="Chủ đề", required=True)
    body = fields.Html(string="Nội dung", required=True)
    sent_date = fields.Datetime(string="Ngày gửi", readonly=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
        ('failed', 'Lỗi')
    ], string="Trạng thái", default="draft", readonly=True)

    @api.depends('recipient_ids')
    def _compute_recipient_emails(self):
        """Cập nhật danh sách email dựa trên người nhận được chọn."""
        for record in self:
            record.recipient_emails = ', '.join(record.recipient_ids.mapped('email'))

    def send_email(self):
        """Gửi email đến tất cả người nhận đã chọn"""
        if not self.recipient_ids or not self.subject or not self.body:
            raise UserError("Vui lòng nhập đầy đủ thông tin trước khi gửi.")

        try:
            mail_values = {
                'subject': self.subject,
                'body_html': self.body,
                'email_to': self.recipient_emails,
                'email_from': self.env.user.email,
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

            # Cập nhật trạng thái sau khi gửi
            self.write({'state': 'sent', 'sent_date': fields.Datetime.now()})
        except Exception:
            self.write({'state': 'failed'})
            raise UserError("Có lỗi xảy ra khi gửi email.")
