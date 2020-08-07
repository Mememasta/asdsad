
// функция вызова окна
function show_popap(id_popap) {
    var id = "#" + id_popap;
    $(id).addClass('active');
    OffScroll (); //Запустили отмену прокрутки
  }
   
  // функция закрытия окна 
  $(".close_popap").click( function(){
    $(".overlay").removeClass("active");
    $(window).unbind('scroll'); //Выключить отмену прокрутки
  });
  
  function OffScroll() {
      var winScrollTop = $(window).scrollTop();
      $(window).bind('scroll',function () {
          $(window).scrollTop(winScrollTop);
      })
  ;}
  
  