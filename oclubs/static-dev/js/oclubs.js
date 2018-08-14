(function($) {
  $(document)
    .ready(function() {

      $('.clickable')
        .click(function() {
          window.location = $(this)
            .data('href');
        });

      $('tr.clickable > td')
        .wrapInner(function() {
          return $('<a class="clickable-a">')
            .attr('href', $(this)
              .parent()
              .data('href')
            );
        });

      $('div.clickable')
        .wrap(function() {
          return $('<a class="clickable-a">')
            .attr('href', $(this)
              .data('href')
            );
        });

      $('#updatecheck')
        .click(function() {
          event.preventDefault();
          $( '.modal .btn-primary' ).hide();
          var checked = $('#leader_radio input[type=radio]:checked');
          var label = $("label[for='" + checked.attr('id') + "']");
          if (checked.size() > 0) {
            $('.modal .modal-body p')
              .html('New leader: ' + label.html());
            $( '.modal .btn-primary' ).show();
          } else {
            $('.modal .modal-body p')
              .text('No selection made.');
            $( '.modal .btn-primary' ).hide();
          }
        });

      $('#updatequit')
        .click(function() {
          var selected = $('.form-group select option:selected');
          $('.modal .modal-body p')
            .text('Your choice is ' + selected.text() + '.');
          $('#clubs')
            .val($('#_clubs')
              .val());
          $('#reason')
            .val($('#_reason')
              .val());
        });

      $('.refresh')
        .click(function() {
          location.reload();
        });

      $('form #picture, form #excel')
        .change(function() {
          var files = $('#picture').prop('files')
          var filenames = $.map(files, function(val) {
            return val.name;
          });

          var retstr = '<br>'

          for (var i = 0; i < filenames.length; i++) {
            retstr = retstr + filenames[i] + '<br>'
          }

          console.log(retstr);

          $(this)
            .closest('form')
            .find('#upload_content')
            .append(retstr);
        });

      if (/\/user\/change_info/.test(window.location.href)) {
        var initView, initEdit;
        initView = function(item, content) {
          item.empty()
            .append($('<div class="col-sm-8 content"><p></p></div>'))
            .append($('<div class="col-sm-4 edit"><a class="clickable">Edit</a></div>'));
          item.find('p')
            .text(content);
          item.find('a')
            .click(function() {
              initEdit(item, content);
            });
        };
        initEdit = function(item, content) {
          item.empty()
            .append($('<div class="col-sm-8 content"><input type="text" class="input_content" name="content"></div>'))
            .append($('<div class="col-sm-4 edit"><a class="clickable">Edit</a></div>'));
          item.find('input.input_content')
            .attr('value', content)
            .focus();
          item.find('.edit')
            .empty()
            .append($('<button class="btn btn-success"><span class="glyphicon glyphicon-ok"></span></button>'))
            .append($('<button class="btn btn-danger"><span class="glyphicon glyphicon-remove"></span></button>'));
          item.find('.edit .btn-success')
            .click(function() {
              var newContent = $(item)
                .find('.input_content')
                .val();
              $.post('/user/change_user_info/submit', {
                  userid: $(item)
                    .closest('tr')
                    .find('.userid')
                    .text(),
                  type: item.data('property-type'),
                  content: newContent,
                  _csrf_token: $(item)
                    .closest('table')
                    .data('csrf')
                })
                .done(function(data) {
                  if (data.result === 'success') {
                    initView(item, newContent);
                  } else {
                    initView(item, content);
                    alert(data.result);
                  }
                });
            });
          item.find('.edit .btn-danger')
            .click(function() {
              initView(item, content);
            });
        };
        $('#admin_user_table td.admin_user_info')
          .each(function() {
            var item = $(this);
            initView(item, item.text());
          });
      }

      $('#floatmenu')
        .click(function() {
          var halfscr = (document.body.clientWidth / 2) + 'px';
          $('#sidenav, #emptyclose')
            .css('width', halfscr);
          $('#emptyclose')
            .css('left', halfscr);
          $('#floatmenu')
            .fadeOut();
        });

      $('#emptyclose, #closebtn')
        .click(function() {
          $('#sidenav, #emptyclose')
            .css('width', '0');
          $('#floatmenu')
            .fadeIn();
        });

      $('.large_container select.mobileselect')
        .change(function() {
          window.location = this.value;
        });

      window.onscroll = function() {
        show_scroll_to_top_btn();
      };

      $('a[href*=\\#]').on('click', function(event) {
        event.preventDefault();
        $('html, body').animate({
          scrollTop: 0
        }, 'slow', function() {});
      });

      $('#search_bar_beside_title')
        .hover(function() {
          $('.search_textbox').addClass('highlighted')
          $('#search_btn').addClass('btn-primary').removeClass('btn-default');
        })
        .mouseleave(function() {
          $('.search_textbox').removeClass('highlighted')
          $('#search_btn').addClass('btn-default').removeClass('btn-primary');
        });

      if (localStorage.theme) {
        document.getElementById("body").className = localStorage.theme;
      } else {
        localStorage.theme = 'day-mode';
      }

      toggle_day_night_btn(localStorage.theme);

      $('#day-night-toggle').click(function() {
        event.preventDefault();
        $('#day-night-toggle').blur();
        toggle_day_night();
      });

      $('.btn_stop_default').click(function() {
        event.preventDefault();
      });

    });
}(jQuery));

$(document).on('click', '.navbar-collapse.in', function(e) {
  if ($(e.target).is('a')) {
    $(this).collapse('hide');
  }
});

function show_scroll_to_top_btn() {
  if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
    document.getElementById('scroll_to_top_btn').style.display = "block";
  } else {
    document.getElementById('scroll_to_top_btn').style.display = "none";
  }
}

function toggle_day_night() {
  // set body class
  var body = document.getElementById("body");
  var currentClass = body.className;

  body.className = currentClass == "day-mode" ? "night-mode" : "day-mode";
  console.log(body.className);
  toggle_day_night_btn(body.className);

  // save preference to local storage
  localStorage.theme = body.className;
}

function toggle_day_night_btn(currentClass) {
  display = currentClass == "day-mode" ? "Night theme" : "Day theme";
  $("#day-night-toggle").html(display);
}
