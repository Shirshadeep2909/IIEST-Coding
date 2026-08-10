async function send() {

    let box = document.getElementById("msg");

    let text = box.value.trim();

    if (text === "")
        return;


    let chat = document.getElementById("chat");


    // Display user message
    chat.innerHTML +=
    `
    <div class="user">
        ${text}
    </div>
    `;


    box.value = "";

    // Keep cursor in input box
    box.focus();


    // Display loading message
    let loading =
    document.createElement("div");

    loading.className = "ai";

    loading.innerHTML = "Thinking...";

    chat.appendChild(loading);


    chat.scrollTop = chat.scrollHeight;



    try {

        let response = await fetch(
            "/chat",
            {
                method: "POST",

                headers:
                {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(
                {
                    message: text,

                    mode:
                    document.getElementById("mode").value
                })
            }
        );


        let data = await response.json();


        // Replace Thinking with AI response
        loading.innerHTML = marked.parse(data.reply);


    }

    catch(error) {

        loading.innerHTML =
        "⚠️ Error connecting to AI";

        console.log(error);

    }


    chat.scrollTop = chat.scrollHeight;

}



// Press Enter to send message
document.getElementById("msg").addEventListener(
    "keydown",
    function(event) {

        if(event.key === "Enter") {

            send();

        }

    }
);