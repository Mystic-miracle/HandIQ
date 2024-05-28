css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="data:image/png;base64,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" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''
ext_template='''<div class="chat-message bot">
  <div class="avatar">
    <img src="assets\\bot.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
  </div>
  <div class="message">{{MSG}}</div>
  <div class="buttons">
    <button id="yes-button">YES</button>
    <button id="no-button">NO</button>
  </div>
</div>'''
user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="assets/shrug.png>
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
