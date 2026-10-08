async function send(){


let box=document.getElementById("msg");


let text=box.value.trim();



if(text==="")
return;



let chat=document.getElementById("chat");



chat.innerHTML +=

`
<div class="user">
${text}
</div>
`;



box.value="";


box.focus();



let loading=document.createElement("div");


loading.className="ai";


loading.innerHTML="Thinking...";


chat.appendChild(loading);



chat.scrollTop=chat.scrollHeight;



try{


let response=await fetch(

"/chat",

{

method:"POST",

headers:{

"Content-Type":"application/json"

},


body:JSON.stringify({

message:text,

mode:
document.getElementById("mode").value

})

}

);



let data=await response.json();



loading.innerHTML=
marked.parse(data.reply);



}



catch(error){


loading.innerHTML=
"⚠️ Unable to connect to AI";


console.log(error);


}



chat.scrollTop=
chat.scrollHeight;


}





// ENTER TO SEND


document
.getElementById("msg")
.addEventListener(

"keydown",

function(event){


if(event.key==="Enter"){

send();

}


}

);

function newChat(){

    let chat = document.getElementById("chat");

    chat.innerHTML = `

    <div class="welcome">

        <div class="welcome-icon">
        🤖
        </div>

        <h1>
        How can I help you?
        </h1>

        <p>
        Ask me about coding, learning, ideas and more.
        </p>

    </div>

    `;

}