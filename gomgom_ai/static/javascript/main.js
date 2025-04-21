const content = "오늘은 뭘 먹을까?";
const text = document.querySelector(".text");
let i = 0;

function typing() {
    if (i < content.length) {
        let txt = content.charAt(i);
        text.innerHTML += txt;
        i++;
    }
}
setInterval(typing, 200)
if (i < content.length) {
    let txt = content.charAt(i);
    text.innerHTML += txt;
    i++;
} else {
    document.querySelector(".blink").style.opacity = 1;
}
