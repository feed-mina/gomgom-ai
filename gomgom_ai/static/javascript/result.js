 
        let data = JSON.parse(JSON.stringify(elice));
        console.log(data)
       console.log(JSON.stringify(elice))
       let elicedata = JSON.stringify(elice);
        console.log(data.length)
        const newhref = window.location.href;
        const url = new URL(newhref);
        const urlParams = url.searchParams;
        const id1  = urlParams.get('id1'); 
        const id2 =  urlParams.get('id2');
        const id3 =  urlParams.get('id3');
        const id4 = urlParams.get('id4');
        
        console.log(newhref);
        console.log(id1)
        console.log(id2)
        console.log(id3)
        console.log(id4)

        
const result = document.querySelector('.result');
const result_text = document.createElement('p');
const othermenu = document.querySelector('.othershow');
 
let itemarray2 = [];
 data.forEach((item, index) =>{  
   /*   console.log(item)*/
   let itemarray = item.id1
   let arr1 = itemarray.split(', ');
   let item4array = item.id4
   let arr4 = item4array.split(', ');
    
   for(let f = 0; f<arr1.length; f++){
    if(arr1[f] == id1){   
            if(item.id2 == id2 && item.id3 == id3){
                console.log('test_id2',item.id2)
                console.log('id3', item.id3)
                for(let q = 0; q<arr4.length; q++){
                    if(arr4[q] == id4){
                         /* console.log('id4',arr4[q]) */
                        /*  console.log('test_id4',item.id4)*/
                    
                        const item_menu = item.menu
                        console.log('menu',item_menu)
                        
                       
                        itemarray2.push(item_menu)
                        console.log('array',itemarray2);
                        console.log('array00',itemarray2[0]);
                       
                        console.log(itemarray2.length);
                        const menu_randomindex = Math.floor(Math.random() * itemarray2.length );
                       console.log('randomindex', menu_randomindex);
                       console.log('random_menu',itemarray2[menu_randomindex]);

                       const random_menu = itemarray2[menu_randomindex];
                       result_text.style.fontSize = '2em';
                       result_text.textContent = `${random_menu}`;
                       result.appendChild(result_text);
                     
                    }
                    if(arr4[q] !=id4 || item.id2 != id2 ||item.id3!= id3){
                        console.log('결과없음')
                        console.log('결과가 없습니다')
                        result_text.style.fontSize = '2em';
                        result_text.textContent = '다시한번 더';
                        result.appendChild(result_text);
                    }
                    else{
                      console.log('결과 없다')
                    }
                    function othershow(){
                        window.location.reload();
                      
                        result_text.style.fontSize = '2em';
                        result_text.textContent = `${random_menu}`;
                        result.appendChild(result_text);
                    }
         
                    
                }
         
            } 
         
        }
    }
})
