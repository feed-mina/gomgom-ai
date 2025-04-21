let data = JSON.parse(JSON.stringify(elice));
console.log(data)

const newhref = window.location.href;
const url = new URL(newhref);
const urlParams = url.searchParams;
const id1  = urlParams.get('id1'); 
const id2 =  urlParams.get('id2');
const id3 =  urlParams.get('id3');
const id4 = urlParams.get('id4');
const id5 =  urlParams.get('id5');
const id6 =  urlParams.get('id6')
console.log(newhref);
console.log('1',id1)
console.log('2',id2)
console.log('3',id3)
console.log('4',id4)
console.log('5',id5)
console.log('6',id6)
let sum = 0
let plus = 0
if(id1=='answerA'){
    plus += 1
    console.log('A')
    console.log('1',plus)
}if(id2=='answerA'){
    console.log('A')
    console.log('2',plus)
}
console.log('2', plus)
if(id3 =='answerA'){
    plus += 1
    console.log('A')
    console.log('3', plus)
}
console.log('3',plus)
if(id4=='answerA'){
    plus += 1
    console.log('A')
    console.log('4',plus)
}
console.log('4',plus)
if(id5=='answerA'){
    plus += 1
    console.log('A')
    console.log('5',plus)
}
console.log('5',plus)
if(id6=='answerA'){
    plus += 1
    console.log('A')
    console.log('6',plus)
}
console.log('6',plus)
sum += plus
console.log('sum',sum)
const result = document.querySelector('.result');
const result_text = document.createElement('p');
const choice = document.querySelector('.choice');
const choice_text = document.createElement('p');

if(sum == 1){
    result_text.textContent = 'gourmet'
}
if(sum == 2){
    result_text.textContent= 'wellBeing'
}
if(sum == 3){
    result_text.textContent = 'childTaste'
}
if(sum == 4){
    result_text.textContent = 'hipster'
}
if(sum == 4 && id3 == 'answerB'){
    result_text.textContent = 'wellKnow'
}

 
data.forEach((item, index) =>{
    let testresult = item.test_result;
    let arr_testresult = testresult.split(', ');
/*    console.log(index, arr_testresult) */
   /*  console.log(arr_testresult.length) */
   for( let v = 0; v<arr_testresult.length; v++){
    console.log(arr_testresult[0])
    if(arr_testresult[v] == result_text){
        console.log(arr_testresult[v]);
    }
   }
})
result.appendChild(result_text);
choice.appendChild(choice_text);
