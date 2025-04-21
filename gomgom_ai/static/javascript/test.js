//제시된 데이터

var data = {
    items:  [{
        name:'혼밥',
        id:1
    },  {
        name:'가족',
        id:2
    }, {
        name:'연인',
        id:3
    }]
};

//위에 제시된 데이터 배열을 지시사항에 따라 div 목록으로 렌더링합니다.
var boxItems= document.getElementsByTagName('button');
console.log(data.items[1].name)

for (var i=0; i<3; i++ ){
    boxItems[i].item_name = data.items[i].name;
    boxItems[i].group_name = data.items[i].group;
    boxItems[i].addEventListener("click", activateItem);
}

function activateItem() {
    sessionStorage.setItem('choice1',this.item_name);
    alert("Hi, "+this.item_name+"!  You are in group " + this.group_name); // console.log() 값이 띄워지는 부분을 확이하는 역할로 보통 쓰임. 
    console.log(sessionStorage.getItem('choice1'))
}