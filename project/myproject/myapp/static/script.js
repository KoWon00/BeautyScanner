window.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('image-input').addEventListener('change', function(event) {
        var fileInput = event.target;
        processImageInput(fileInput);
    });

    var imageInput = document.getElementById('image-input');
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            var fileInput = event.target;
            processImageInput(fileInput);
        });
    } 
    
    document.getElementById('close-button').addEventListener('click', function() {
        document.querySelector('.chatbot').style.display = 'none';
    });

    document.querySelector('nav a[href="#products"]').addEventListener('click', function(event) {
        document.getElementById('chatbot').style.display = 'block';
    });    

    function addMessage(message, role) {
        var messageElement = document.createElement('p');
        messageElement.textContent = message;
        var messageWrapper = document.createElement('div');
        messageWrapper.classList.add('chatbot-message', `chatbot-message-${role}`);
        messageWrapper.appendChild(messageElement);
        var chatBody = document.querySelector('.chatbot-body');
        chatBody.appendChild(messageWrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function processUserInput(userInput) {
        document.getElementById('chatbot-input').value = '';
        addMessage(userInput, 'user');
        fetch('/chat/', {
            method: 'POST',
            body: JSON.stringify({ 'message': userInput }),
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            //addMessage(data['response'], 'bot');
            setTimeout(function() {
                addMessage(data['response'], 'bot');
            }, 1000);
        });
    }    

    document.getElementById('chatbot-input').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            var userInput = document.getElementById('chatbot-input').value;
            processUserInput(userInput);
        }
    });

    document.getElementById('send-button').addEventListener('click', function(e) {
        e.preventDefault();
        var userInput = document.getElementById('chatbot-input').value;
        processUserInput(userInput);
    });

    document.getElementById('image-upload-form').addEventListener('submit', function(e) {
        e.preventDefault();
    
        var formData = new FormData();
        formData.append('image', document.querySelector('input[type=file]').files[0]);
    
        fetch('/upload_image/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addMessage(data.error, 'bot');
            } else {
                var ingredients = data.result.ingredients.join('\n');
                var allergy = data.result.allergy;
                var harmful = data.result.harmful;
                var recommended_products = data.result.recommended_products;
                addMessage('성분: \n' + ingredients, 'bot');
                setTimeout(() => {
                    addMessage('알레르기 유발 성분: ' + allergy, 'bot');
                    addMessage('유해성분: ' + harmful, 'bot');
                    addMessage('추천 제품: ', 'bot');
                }, 1000);
                for (var i = 0; i < recommended_products.length; i++) {
                    (function(i) {
                        var product = recommended_products[i];
                        setTimeout(() => {
                            addMessage((i+1) + '순위: ' + product.name + ', 유사도: ' + product.similarity.toFixed(2) + '%', 'bot');
                        }, 1000 * (i+1));
                    })(i);
                }
            }
        });
    });
    
    document.getElementById('image-input').addEventListener('change', function(event) {
        var fileInput = event.target;
        processImageInput(fileInput);
    });
    
    function processImageInput(fileInput) {
        var formData = new FormData();
        formData.append('image', fileInput.files[0]);
    
        fetch('/upload_image/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            setTimeout(() => {
                //addMessage('성분을 확인하였습니다.', 'bot');
                //addMessage('알레르기 검출, 유해성분 발견, 유사제품 추천 중 무엇을 원하시나요?', 'bot');
            }, 3000);
        });
    }
    
});