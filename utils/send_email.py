import smtplib
from email.mime.text import MIMEText
from email.header import Header
from MttmView.settings import smtp_server, smtp_port, sender_email, auth_code


def send_email(email, content_type):
    # 收件人和内容
    receiver_email = email
    subject = "【市场趋势客观提示】黄金整体趋势更新"
    content = f"""
尊敬的会员：

您好！基于您订阅的服务内容，现客观提示：当前黄金市场整体趋势为：{content_type}

本信息仅作趋势状态同步，不构成任何交易建议。

[您的公司名称]
2026年5月15日
    """

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = Header(sender_email)
    msg['To'] = Header(receiver_email)
    msg['Subject'] = Header(subject, 'utf-8')

    try:
        # 2. 连接服务器并发送
        # 使用 SSL 上下文连接
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, auth_code)
        server.sendmail(sender_email, [receiver_email], msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送失败: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    send_email("qiuqi@klipc.com", "下行")