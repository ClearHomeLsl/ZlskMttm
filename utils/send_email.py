import smtplib
from email.mime.text import MIMEText
from email.header import Header

# --- 配置信息 (请替换为你的实际信息) ---
smtp_server = "smtp.qiye.163.com"  # 网易企业邮箱服务器
smtp_port = 465  # SSL端口
sender_email = "hr@yourcompany.com"  # 你的企业邮箱全称
auth_code = "xxxxx"  # 上一步生成的客户端授权码，不是登录密码
receiver_email = "someone@example.com"
# -----------------------------------

# 构建邮件内容
html_content = """
<html>
  <body>
    <h3>Python 测试报告</h3>
    <p>本次测试执行完毕，结果如下：</p>
    <table border="1">
      <tr><th>用例</th><th>结果</th></tr>
      <tr><td>登录测试</td><td><span style="color:green;">通过</span></td></tr>
    </table>
  </body>
</html>
"""

# 使用 MIMEText 构建邮件，指定编码为 utf-8
msg = MIMEText(html_content, 'html', 'utf-8')
msg['From'] = Header(sender_email)
msg['To'] = Header(receiver_email)
msg['Subject'] = Header("自动化测试报告 - HTML格式")

try:
    # 连接服务器 (使用 SSL)
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    # 打印与服务器的通信信息（可选，用于调试）
    # server.set_debuglevel(1)

    # 登录
    server.login(sender_email, auth_code)

    # 发送邮件
    server.sendmail(sender_email, [receiver_email], msg.as_string())

    print("邮件发送成功！")
except Exception as e:
    print(f"发送失败: {e}")
finally:
    server.quit()  # 断开连接