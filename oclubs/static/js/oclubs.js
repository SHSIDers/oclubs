( function( $ ) {
	$( document )
		.ready( function() {
			$( ".clickable" )
				.click( function() {
					window.document.location = $( this )
						.data( "href" );
				} );

			$( "#updatecheck" )
				.click( function() {
					var checked = $( '#leader_radio input[type=radio]:checked' );
					if ( checked.size() > 0 ) {
						$( ".modal .modal-body" )
							.html( "<p>Your choice is " + checked.val() + ".</p>" );
						$( ".modal .modal-footer" )
							.html( "<button type='button' class='btn btn-default' data-dismiss='modal'>Reselect</button>" +
									'<input type="submit" class="btn btn-primary" form="leader_radio" name="change_leader" value="Confirm">' );
					} else {
						$( ".modal .modal-body" )
							.html( "<p>Please select one memeber as next club leader!</p>" );
						$( ".modal .modal-footer" )
							.html( "<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>" );
					}
				} );

			$( "#updatequit" )
				.click( function() {
					var selected = $( '.form-group select option:selected' );
					if ( selected.size() > 0 ) {
						$( ".modal .modal-body" )
							.html( "<p>Your choice is " + selected.text() + ".</p>" );
					} else {
						$( ".modal .modal-body" )
							.html( "<p>Please choose the club you want to quit.</p>" );
					}
				} );

			$( ".updatehm" )
				.click( function() {
					var date = $( "#date" ).val();
					var contents = $( "#contents" ).val();
					if ( date !== '' && contents !== '' ) {
						$( "#schedule tbody" )
							.append( "<tr><td>" + date + "</td><td>" + contents + "</td><td><button class='btn btn-primary' id='" + contents + "'>Delete</button></td></tr>");
						$( "#" + contents )
							.click( function() {$( this ).parents("tr").eq(0).remove();});
					}
				} );

			$( '.refresh' )
				.click( function() {
					location.reload();
				} );

			$( '.drag' )
				.draggable( {
					handle:'.drag-point',
					containment: '.homepage_image',
					stack: '.drag',
					revert: true
				} );
		} );
} )( jQuery );


var menuYloc = null;
	$(document).ready(function(){
		document.querySelector('#floatmenu').style.left = (window.innerWidth -75) + "px"
		document.querySelector('#floatmenu').style.top = (window.innerHeight -125) + "px"
		menuYloc = parseInt($('#floatmenu').css("top").substring(0,$('#floatmenu').css("top").indexOf("p")))
			$(window).scroll(function () {
				if(window.innerWidth<=500){
					document.querySelector('#floatmenu').style.top = menuYloc+$(document).scrollTop()+"px";
				}
			});
			$(window).resize(function () {
				if(window.innerWidth<=500){
					document.querySelector('#floatmenu').style.left = (window.innerWidth -75) + "px";
					document.querySelector('#floatmenu').style.top = (window.innerHeight -125) + "px";
				}
			});
	})