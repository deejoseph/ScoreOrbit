"""邮件通知模块 - 发送学习报告"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List

class EmailNotifier:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_learning_report(self, student_name: str, parent_email: str, 
                             report_data: Dict) -> bool:
        """发送学习报告"""
        
        subject = f"【ScoreOrbit】{student_name} 生物学习报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 构建HTML邮件内容
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .report {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .score {{ font-size: 48px; color: #4CAF50; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .weak-point {{ color: #f44336; }}
                .strong-point {{ color: #4CAF50; }}
            </style>
        </head>
        <body>
            <div class="report">
                <div class="header">
                    <h2>ScoreOrbit 学习报告</h2>
                    <p>{student_name} 同学</p>
                    <p>{datetime.now().strftime('%Y年%m月%d日')}</p>
                </div>
                
                <div class="section">
                    <h3>📊 本次练习概况</h3>
                    <p>得分: <span class="score">{report_data.get('score', 0)}/{report_data.get('total', 0)}</span></p>
                    <p>正确率: {report_data.get('percentage', 0):.1f}%</p>
                    <p>练习数量: {report_data.get('question_count', 0)} 题</p>
                </div>
                
                <div class="section">
                    <h3>📝 错题分析</h3>
                    <ul>
                        {''.join([f'<li class="weak-point">{err}</li>' for err in report_data.get('errors', [])])}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>🎯 建议强化方向</h3>
                    <ul>
                        {''.join([f'<li>{sug}</li>' for sug in report_data.get('suggestions', [])])}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>💡 学习建议</h3>
                    <p>{report_data.get('advice', '继续保持！')}</p>
                </div>
                
                <p style="text-align: center; color: #888; margin-top: 30px;">
                    —— 本报告由 ScoreOrbit AI家教系统自动生成 ——
                </p>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = parent_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def send_daily_summary(self, student_name: str, parent_email: str,
                           daily_data: Dict) -> bool:
        """发送每日学习总结"""
        # 简化版，与send_learning_report类似
        return self.send_learning_report(student_name, parent_email, daily_data)


# 测试
if __name__ == "__main__":
    # 配置邮箱（需要替换成真实信息）
    notifier = EmailNotifier(
        smtp_server="smtp.qq.com",  # QQ邮箱
        smtp_port=465,
        sender_email="your_email@qq.com",
        sender_password="your_auth_code"
    )
    
    test_report = {
        'score': 8,
        'total': 10,
        'percentage': 80,
        'question_count': 10,
        'errors': ['蛋白质计算错误', '光合作用过程混淆'],
        'suggestions': ['复习蛋白质章节', '重温光合作用图解'],
        'advice': '基础扎实，继续加强计算题训练'
    }
    
    # notifier.send_learning_report("小明", "parent@example.com", test_report)
    print("邮件模块已就绪，配置后即可使用")