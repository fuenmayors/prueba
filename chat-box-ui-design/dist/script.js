var ischatopen = false;
var ele = document.getElementById("chatbar");

function openChatBox()
{
  if(ischatopen == false)
    {
       ele.classList.add("toggle");
       ischatopen = true;
       document.getElementById("chatOpen").classList.remove("fa-comments");
document.getElementById("chatOpen").classList.add("fa-times");
      
    }
  else {
     ele.classList.remove("toggle");
     ischatopen = false;
    document.getElementById("chatOpen").classList.add("fa-comments");
document.getElementById("chatOpen").classList.remove("fa-times");
  }
}

//url(https://i.pinimg.com/originals/40/39/e0/4039e0f1ef08b7b965bacb4641a7af49.jpg);

function send()
{
  console.log("Here");
  var chatBody = document.getElementById("chatBody");
  var Clientmsg = document.getElementById("MsgInput").value;  
  document.getElementById('MsgInput').value = '';
  var divClient = document.createElement("div");
  divClient.classList.add("chat_box_body_self");
  
  divClient.innerHTML = Clientmsg;
  
  chatBody.append(divClient);
  
  
  var divBot = document.createElement("div");
  divBot.classList.add("chat_box_body_other");
  
  divBot.innerHTML = Clientmsg;
  setTimeout(function(){
  $('divBot').show();
}, 5000);
  chatBody.append(divBot);
  chatBody.scrollTop = chatBody.scrollHeight;
}