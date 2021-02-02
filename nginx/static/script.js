"use strict";

var messages_block = document.getElementById('messages_block');
var left_block = document.getElementById('left_block');
var right_block = document.getElementsByClassName('right_block');

/* функция настраивает размеры html элементов в зависимости от размера окна пользователя */
function resize() {
	var window_height = window.innerHeight;
	var main_wrap = document.getElementById('main_wrap');
	var messages_block_wrap = document.getElementById('messages_block_wrap');
	var settings_body = document.getElementsByClassName('settings-body');
	var contacts_body = document.getElementsByClassName('contacts-body');
	var user_info_body = document.getElementsByClassName('user_info_body');
	var conversation_body = document.getElementsByClassName('conversation-body');

	main_wrap.style.height = window_height;
	left_block.style.height = window_height-50;
	right_block[0].style.height = window_height-50;
	if (messages_block){
		messages_block_wrap.style.height = window_height-190;
		messages_block.style.maxHeight = window_height-190;
	}
	settings_body[0].style.maxHeight=window_height-190;
	contacts_body[0].style.maxHeight=window_height-190;
	if (user_info_body[0]) {
		user_info_body[0].style.maxHeight=window_height-220;
	}
	conversation_body[0].style.maxHeight=window_height-190;

	if (user_info_body[1]){
		user_info_body[1].style.maxHeight=window_height-220
	}
	if (messages_block) {
		messages_block.scrollTop = messages_block.scrollHeight;
	}
	
}
/* получение новых сообщений в открытом диалоге, обновление списка диалогов в левой части сайта */
async function new_messages(){
	var dialog_id = right_block[0].id;
	var response = await fetch('/check_new_messages',{
		method: 'POST',
		headers: {
		'Content-Type': 'application/json;'
		},
		body: JSON.stringify(dialog_id)
	});
	var result = await response.json();
	/* получение новых сообщений в открытом диалоге */
	if (result.messages) {
		messages_block.insertAdjacentHTML('beforeend', result.messages)
		messages_block.scrollTop = messages_block.scrollHeight;;
	}
	/* обновление списка диалогов. */
	if (result.left_messages){
		left_block.insertAdjacentHTML('afterbegin', result.left_messages)
		var left_block_ids = [];
		for (var i=0; i<result.count; i++){ /* Добавляем в массив id всех новых элементов*/
			left_block_ids.push(left_block.children[i].id)
		}
		var left_block_count = left_block.childElementCount; 
		var remove_arr = [] 
		for (var i=result.count; i<left_block_count; i++){ /* находим старые элменты, у которых id совпадает с новыми */
			if (left_block_ids.includes(left_block.children[i].id)) {
				remove_arr.push(left_block.children[i])
			}
		}
		for (var i=0; i<remove_arr.length; i++){ /* удаляем их */
			left_block.removeChild(remove_arr[i]);
		}
	}
};

/* отправка сообщения, отображение своего сообщения*/
async function send_message(){
	var textarea = document.getElementById('textarea');
	var data = {
		textarea_data: textarea.value,
		dialog_id : right_block[0].id
	}
	var response = await fetch('/send_message',{
		method: 'POST',
		headers: {
		'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (response.ok) {
		var result = await response.text();
		if (result) {
			messages_block.insertAdjacentHTML('beforeend', result)
			messages_block.scrollTop = messages_block.scrollHeight;;
		}
	}
};

/* функция подгрузки старых сообщений */
async function get_more_messages(){
	var data = {
		dialog_id: right_block[0].id,
		count: messages_block.childElementCount
	};
	var response = await fetch('/get_more_messages', {
		method: 'POST',
		headers: {
		'Content-Type': 'application/json;'
		},
		body: JSON.stringify(data),
	});
	if (response.ok) {
		var result = await response.text();
		if (result) {
			var last_message = messages_block.firstElementChild;
			messages_block.insertAdjacentHTML('afterbegin', result);
			last_message.scrollIntoView()
		}
	}
}
/* подгружать старые сообщения, если скролл достиг верха */
function get_more_messages_wrap(){
	if (messages_block.scrollTop==0){
	get_more_messages()}
}
/* функция, отображающая информацию о пользователе при клике на ник */
async function get_user_info(id){
	var response = await fetch('/get_user_info', {
		method: 'POST',
		headers: {
		'Content-Type': 'application/json;'
		},
		body: JSON.stringify(id)
	});
	if (response.ok) {
		var result = await response.text();
		if (result) {
			document.body.insertAdjacentHTML('beforeend', result);
		}
	}
	var u_inf = document.getElementById('user_info');
	var u_inf_cl = document.getElementById("user_info_close");
	u_inf.style.display = 'block';
	document.getElementsByClassName('user_info_body')[1].style.maxHeight = window.innerHeight-220;
	u_inf_cl.onclick = function() {
		u_inf.remove()
	}

	window.addEventListener('click', function(event) { 
		if (event.target == u_inf) {
			u_inf.remove()
		}
	});
}
/* создание беседы */
async function create_conversation(contacts_array){
	var textarea_value = document.getElementById('conversation-name-textarea').value
	var data = {
		textarea_data: textarea_value,
		contacts : contacts_array
	}
	var response = await fetch('/create_conversation',{
		method: 'POST',
		headers: {
		'Content-Type': 'application/json'
		},
		body: JSON.stringify(data),
		redirect: "follow"
	});
	if (response.ok) {
	var result = await response.json();
	window.location.href = result.redirect;
	}
};
/* подгоняем элементы страницы под размеры окна пользователя при загрузке страницы */
resize();

/* подгоняем элементы страницы под размеры окна при изменении окна пользователем вручную */
window.addEventListener('resize', function(event) { 
	resize();
});

/* проверка новых сообщений и их отображение, каждые 1000мс */
setInterval("new_messages()", 1000);


/* ниже функции открытия/закрытия разных модальных окон при кликах*/
var contacts = document.getElementById('contacts');
var contacts_link = document.getElementById("contacts-link");
contacts_link.onclick = function() {
    contacts.style.display = "block";
}

var contacts_close = document.getElementsByClassName("contacts-close")[0];
contacts_close.onclick = function() {
	contacts.style.display = "none";
}

window.addEventListener('click', function(event) { 
	if (event.target == contacts) {
		contacts.style.display = "none";
	}
});

var settings = document.getElementById('settings');
var s_link = document.getElementById('settings-link');
s_link.onclick = function() {
    settings.style.display = "block";
}

var s_close = document.getElementById('settings-close');
s_close.onclick = function() {
	settings.style.display = "none";
}

window.addEventListener('click', function(event) { 
	if (event.target == settings) {
		settings.style.display = "none";
	}
});

var dd_menu = document.getElementById("dd-menu");
var menu_pic = document.getElementById("menu_pic");
window.addEventListener('click', function(event) { 
	if (event.target.className != 'logo-wrap' &&
		event.target.className != 'logo' &&
		event.target.className != 'menu_pic' &&
		event.target.className != 'logo-text') {
		dd_menu.style.display = 'none';
		menu_pic.textContent = "≡";

	}
});
var logo_wrap = document.getElementById("logo-wrap");
logo_wrap.onclick = function() {
	if (dd_menu.style.display != "block") {
		menu_pic.textContent = "×";
		menu_pic.style.paddingTop = "0";
		dd_menu.style.display = "block";

	} else {
		menu_pic.textContent = "≡";
		menu_pic.style.paddingTop = "2"
		dd_menu.style.display = 'none';
	}
}

var head_right = document.getElementById('head_right');
var u_inf_h = document.getElementById('user_info_head');
if (head_right){
	head_right.onclick = function() {
    	u_inf_h.style.display = "block";
	}
}

var u_inf_h_cl = document.getElementById('user_info_head_close');
if (u_inf_h) {
	u_inf_h_cl.onclick = function() {
		u_inf_h.style.display = "none";
	}

	window.addEventListener('click', function(event) { 
		if (event.target == u_inf_h) {
			u_inf_h.style.display = "none";
		}
	});
}

var conversation = document.getElementById('conversation');
var conversation_link = document.getElementById("conversation-link");
conversation_link.onclick = function() {
    conversation.style.display = "block";
}

var conversation_close = document.getElementsByClassName("conversation-close")[0];
conversation_close.onclick = function() {
	conversation.style.display = "none";
}

window.addEventListener('click', function(event) { 
	if (event.target == conversation) {
		conversation.style.display = "none";
	}
});

/* добавляем в массив id нужных нам пользователей при создании беседы, чтобы потом отправить их серверу */
var contacts_wrap = document.getElementById('contacts_wrap')
var contacts_array = [];
contacts_wrap.onclick = function(event){
	var contact = event.target.closest('.contact-wrap')
	contact.id = Number(contact.id)
	if (contacts_array.includes(contact.id)){
		contact.style.background = 'white';
		var index = contacts_array.indexOf(contact.id);
		if (index > -1) {
		contacts_array.splice(index, 1);
		}
	}
	else{
		contacts_array.push(contact.id);
		contact.style.background = '#ccc';
	}

}
/* не переносить строку при нажатии enter в поле для ввода названия беседы */
var conversation_name_textarea = document.getElementById('conversation-name-textarea')
conversation_name_textarea.onkeydown = function(e) {
	e = e || window.event;
	if (e.keyCode == 13) {
		e.preventDefault();
	}
}
/* создание беседы при нажатии на кнопку */
var conversation_button = document.getElementById('conversation-button')
conversation_button.addEventListener('click', function(event) { 
	create_conversation(contacts_array);
});

/* подгрузка сообщений при скроле */
if (messages_block) {
	messages_block.addEventListener('scroll', get_more_messages_wrap);
}

/* Enter - отправить сообщение, Shift+Enter - перенос строки */
var textarea = document.getElementById('textarea');
var send_button = document.getElementById('send_button');
if (textarea) {
	textarea.onkeydown = function(e) {
		e = e || window.event;
		if (e.shiftKey && e.keyCode == 13) {
			textarea.value += ''

		}
		if (!e.shiftKey && e.keyCode == 13) {
			e.preventDefault();
			send_button.click();
		}
	}
}
/* отображение информации о пользователе при клике на ник */
if (messages_block) {
	messages_block.onclick = function(event) {
		var target = event.target;
		if (target.className == 'message_username') {
			get_user_info(target.id);
		}
	}
}
/* отправка сообщения при нажатии кнопки "Отправить" */
if (send_button) {
	send_button.addEventListener('click', function(event) { 
		send_message();
		textarea.value="";
		textarea.focus();
	});
}
/* смайлики */
var smiles = document.getElementsByClassName('smile');
var arr_smiles = ["\u{1F642}","\u{1F602}","\u{1F609}","\u{1F610}","\u{1F60F}","\u{1F60A}",
	"\u{1F625}","\u{1F618}","\u{1F634}","\u{1F635}","\u{1F633}","\u{1F631}"]

/* добавление смайликов в textarea */
if (textarea){
	for (var i=0; i<arr_smiles.length;i++)(function(i){ 
		smiles[i].onclick = function() {
			textarea.value += arr_smiles[i];
			textarea.focus();
		}
	})(i);
}
