"use strict";
/* этот скрипт подгружается на странице открытого диалога */
var contacts = document.getElementById('contacts');
var contacts_link = document.getElementById("contacts-link");
var contacts_close = document.getElementsByClassName("contacts-close")[0];
var menu_pic = document.getElementById("menu_pic");
var logo_wrap = document.getElementById("logo-wrap");
var dd_menu = document.getElementById("dd-menu");
var settings = document.getElementById('settings');
var s_close = document.getElementById('settings-close');
var s_link = document.getElementById('settings-link');
var u_inf_h = document.getElementById('user_info_head');
var u_inf_h_cl = document.getElementById('user_info_head_close');
var head_right = document.getElementById('head_right');
var messages_block = document.getElementById('messages_block');
var textarea = document.getElementById('textarea');
var send_button = document.getElementById('send_button');
var main_wrap = document.getElementById('main_wrap');
var left_block = document.getElementById('left_block');
var right_block = document.getElementsByClassName('right_block');
var messages_block_wrap = document.getElementById('messages_block_wrap');
var messages_block = document.getElementById('messages_block');
var settings_body = document.getElementsByClassName('settings-body');
var contacts_body = document.getElementsByClassName('contacts-body');
var user_info_body = document.getElementsByClassName('user_info_body');
var smiles = document.getElementsByClassName('smile');

var last_message = messages_block.firstElementChild;
var window_height = window.innerHeight;


/* подгоняем элементы страницы под размеры окна при загрузке страницы */
resize();

/* подгрузка сообщений при скроле */
messages_block.addEventListener('scroll', get_more_messages_wrap);
/* проверка новых сообщений и их отображение, каждые 1000мс */
setInterval("new_messages()", 1000);

/* подгоняем элементы страницы под размеры окна при изменении окна пользователем вручную */
window.addEventListener('resize', function(event) { 
	resize();
});

function resize() {
	window_height = window.innerHeight;
	main_wrap.style.height = window_height;
	left_block.style.height = window_height-50;
	right_block[0].style.height = window_height-50;
	messages_block_wrap.style.height = window_height-190;
	messages_block.style.maxHeight = window_height-190;
	settings_body[0].style.maxHeight=window_height-190;
	contacts_body[0].style.maxHeight=window_height-190;
	user_info_body[0].style.maxHeight=window_height-220;

	if (document.getElementsByClassName('user_info_body')[1]){
		document.getElementsByClassName('user_info_body')[1].style.maxHeight=window_height-220
	}
	messages_block.scrollTop = messages_block.scrollHeight;
}
/* ниже функции открытия/закрытия разных модальных окон при кликах*/
contacts_link.onclick = function() {
    contacts.style.display = "block";
}
contacts_close.onclick = function() {
	contacts.style.display = "none";
}

window.addEventListener('click', function(event) { 
	if (event.target == contacts) {
		contacts.style.display = "none";
	}
});

s_link.onclick = function() {
    settings.style.display = "block";
}

s_close.onclick = function() {
	settings.style.display = "none";
}

window.addEventListener('click', function(event) { 
	if (event.target == settings) {
		settings.style.display = "none";
	}
});

window.addEventListener('click', function(event) { 
	if (event.target.className != 'logo-wrap' &&
		event.target.className != 'logo' &&
		event.target.className != 'menu_pic' &&
		event.target.className != 'logo-text') {
		dd_menu.style.display = 'none';
		menu_pic.textContent = "≡";

	}
});

logo_wrap.onclick = function() {
	if (menu_pic.textContent == "≡") {
		menu_pic.textContent = "×";
		menu_pic.style.paddingTop = "0";
		dd_menu.style.display = "block";

	} else {
		menu_pic.textContent = "≡";
		menu_pic.style.paddingTop = "2"
		dd_menu.style.display = 'none';
	}
}

head_right.onclick = function() {
    u_inf_h.style.display = "block";
}
u_inf_h_cl.onclick = function() {
	u_inf_h.style.display = "none";
}

window.addEventListener('click', function(event) { 
	if (event.target == u_inf_h) {
		u_inf_h.style.display = "none";
	}
});

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
		body: JSON.stringify(data)
	});
	if (response.ok) {
		var result = await response.text();
		if (result) {
			last_message = messages_block.firstElementChild
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
/* Enter - отправить сообщение, Shift+Enter - перенос строки */
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


/* функция, отображающая информацию о пользователе при клике на ник */
messages_block.onclick = function(event) {
	var u_inf
	var u_inf_cl
	var target = event.target;
	if (target.className == 'message_username') {
		async function get_user_info(){
			var id = target.id /* получаем id пользователя */
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
			u_inf = document.getElementById('user_info');
			u_inf_cl = document.getElementById("user_info_close");
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
		get_user_info();
	}
}
/* получение новых сообщений в открытом диалоге, обновление списка диалогов в левой части сайта */
async function new_messages(){
	var left_block = document.getElementById('left_block')
	var dialog_id = document.getElementsByClassName('right_block')[0].id
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
/* отправка сообщения при нажатии кнопки "Отправить" */
send_button.addEventListener('click', function(event) { 
	send_message();
	textarea.value="";
	textarea.focus();
});
/* смайлики */
var arr_smiles = ["\u{1F642}","\u{1F602}","\u{1F609}","\u{1F610}","\u{1F60F}","\u{1F60A}",
	"\u{1F625}","\u{1F618}","\u{1F634}","\u{1F635}","\u{1F633}","\u{1F631}"]

/* добавление смайликов в textarea */
for (var i=0; i<arr_smiles.length;i++)(function(i){ 
	smiles[i].onclick = function() {
		textarea.value += arr_smiles[i]+" ";
		textarea.focus();
	}
})(i);
