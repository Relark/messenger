"use strict";
/* скрипт подгружается на странице /im, когда не выбран диалог*/
var contacts = document.getElementById('contacts');
var contacts_link = document.getElementById("contacts-link");
var contacts_close = document.getElementsByClassName("contacts-close")[0];
var menu_pic = document.getElementById("menu_pic");
var logo_wrap = document.getElementById("logo-wrap");
var dd_menu = document.getElementById("dd-menu");
var settings = document.getElementById('settings');
var s_close = document.getElementById('settings-close');
var s_link = document.getElementById('settings-link');
var textarea = document.getElementById('textarea');
var main_wrap = document.getElementById('main_wrap');
var left_block = document.getElementById('left_block');
var right_block = document.getElementsByClassName('right_block');
var settings_body = document.getElementsByClassName('settings-body');
var contacts_body = document.getElementsByClassName('contacts-body');
var window_height = window.innerHeight;

/* подгоняем элементы страницы под размеры окна при загрузке страницы */
resize();

/* подгоняем элементы страницы под размеры окна при изменении окна пользователем вручную */
window.addEventListener('resize', function(event) { 
	resize();
});
/* каждую секунду проверяем наличие новых сообщений */
setInterval("new_messages()", 1000);

function resize() {
	window_height = window.innerHeight;
	main_wrap.style.height = window_height;
	left_block.style.height = window_height-50;
	right_block[0].style.height = window_height-50;
	settings_body[0].style.maxHeight=window_height-190;
	contacts_body[0].style.maxHeight=window_height-190;
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
/* функция из первого скрипта, здесь нужна только для новых сообщений в левом блоке */
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
	if (result.messages) {
		messages_block.insertAdjacentHTML('beforeend', result.messages)
		messages_block.scrollTop = messages_block.scrollHeight;;
	}
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
