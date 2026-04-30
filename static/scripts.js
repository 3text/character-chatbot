/* scripts.js */

/* グローバル変数 */
const userText = document.querySelector('.user_text') ; 
const chatForm = document.querySelector('form') ;

const indicatorHtml = `<span class="typing_indicator"><span>.</span><span>.</span><span>.</span></span>`;

/* 自動スクロール */
function scrollToBottom() {
	const chatArea = document.querySelector('.chat_area') ;

	if (chatArea) {
		chatArea.scrollTop = chatArea.scrollHeight ;
	}
}

/* 入力フォームの拡張 */
function input_area_exp() {
	if (userText) {
		userText.style.height = 'auto' ;
		userText.style.height = userText.scrollHeight + 'px';
		scrollToBottom();
		}

}


/* ここから非同期 */

/* チャットエリアに追加する */
function appendChatArea( chatArea , element ) {
	chatArea.append(element);
	scrollToBottom();
}

/* 返答待ちのアニメーション */
function startTypingAnimation(parentElement){
	const dots = parentElement.querySelectorAll('.typing_indicator span');

	dots.forEach( (dot , index) => {
		dot.style.animation = "typing_float 2s infinite";
		dot.style.animationDelay = `${index * 0.2}s`;
	});
}

/* オーバーレイを表示する関数 */
function showOverlay(message) {
	const overlay = document.getElementById('errorOverlay');
	const messageElement = document.getElementById('errorMessage');
	if (overlay && messageElement) {
	messageElement.textContent = message;
	overlay.style.display = 'flex'; // 表示する
    }
}

/* オーバーレイを閉じる関数 */
function closeOverlay() {
	const overlay = document.getElementById('errorOverlay');
	if (overlay) overlay.style.display = 'none';
}

/* ユーザーメッセージ */
function appendUserMessage(text) {
	const userDiv = document.createElement('div');
	userDiv.classList.add('user');
	
	userDiv.innerHTML = `
		<div class="icon">❤️</div>
		<div class="message">
			<p class="name">user</p>
			<p class="content"></p>
		</div>	
	`

	userDiv.querySelector('.content').textContent = text ;
	return userDiv;

}

/* モデルメッセージ */
function appendModelMessage(text,name,icon_url) {
	const modelDiv = document.createElement('div') ;
		modelDiv.classList.add('model') ;
	
		modelDiv.innerHTML = `
			<div class="icon">
				<img src ="${icon_url}" alt="icon">
			</div>
							
			<div class="message">
				<p class="name">${name}</p>
				<p class="content">${text}</p>
			</div>
			`;

		return modelDiv;
}



/* 表示 */

if(chatForm) {
	chatForm.addEventListener( 'submit'  , async(e) => {
		e.preventDefault();

		const chatArea = document.querySelector('.chat_area'); 
		if (!chatArea) return ;

		/* モデルの名前とアイコンの呼び出し */
		const modelName = chatArea.dataset.modelName ;
		const modelIcon = chatArea.dataset.modelIcon ;

		const formData = new FormData(chatForm);
		const userMessage = formData.get('user_input')

		if (!userMessage) return ;

		const tempUserMessage = appendUserMessage(userMessage);
		
		/* チャットエリアに追加 */
		appendChatArea(chatArea,tempUserMessage);

		/* 同期処理が始まる前はにmodel側からの返答待ちを知らせる */
		const tempModelMessage = appendModelMessage(indicatorHtml, modelName, modelIcon);
		
		appendChatArea(chatArea,tempModelMessage);	
		startTypingAnimation(tempModelMessage);

		userText.value = '';
		input_area_exp();

		/* 入力の禁止 */
		const sendButton = document.querySelector('.send_button');
		
		userText.disabled = true;
		sendButton.disabled=true;

		try {
			const response = await fetch('/' ,{ 
				"method" : "POST" ,
				"body" : formData
			}) ;

			const data = await response.json();

			if (response.ok) {
				console.log("成功:" , data);	

				const modelMessageContent = tempModelMessage.querySelector('.content');
				if (modelMessageContent) {
					modelMessageContent.textContent = data.model_message ;
					}
			} else {
				// サーバーエラー時：ドットを消してカードを出す
				tempModelMessage.remove(); // 吹き出し自体を消す
				showOverlay(data.message || "エラーが発生しました。");
			}

		} catch(error){
			tempModelMessage.remove();
			showOverlay("サーバーと通信できませんでした。");
		} finally {
			/* 入力フォームの有効化 */
			userText.disabled = false;
			sendButton.disabled = false;

			/* カーソルを戻す */
			userText.focus();
		}
	});
}


/* 関数を叩く */
window.onload = scrollToBottom;

if (userText) {
	userText.addEventListener('input', input_area_exp);

	userText.addEventListener( 'keydown'  , (e) => {
		if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
					e.preventDefault();
					chatForm.requestSubmit();
		}
	});
}