/*
* Greedy Navigation
*
* http://codepen.io/lukejacksonn/pen/PwmwWV
*
*/

var $nav = $('#site-nav');
var $btn = $('#site-nav button');
var $vlinks = $('#site-nav .visible-links');
var $hlinks = $('#site-nav .hidden-links');

function updateNav() {
  // Measure the complete navigation, then keep the section links together.
  $hlinks.children().appendTo($vlinks);

  if ($vlinks.width() > $nav.width()) {
    $vlinks.children().not('.masthead__menu-item--lg').appendTo($hlinks);
    $btn.removeClass('hidden');
  } else {
    $btn.addClass('hidden');
    setMenuOpen(false);
  }
}

function setMenuOpen(open) {
  $hlinks.toggleClass('hidden', !open);
  $btn.toggleClass('close', open).attr('aria-expanded', String(open));
}

$(window).resize(function() {
  updateNav();
});

$btn.on('click', function() {
  setMenuOpen($hlinks.hasClass('hidden'));
});

$(document).on('click', function(event) {
  if (!$nav[0].contains(event.target)) {
    setMenuOpen(false);
  }
});

$nav.on('keydown', function(event) {
  if (event.key === 'Escape' && !$hlinks.hasClass('hidden')) {
    setMenuOpen(false);
    $btn.trigger('focus');
  }
});

updateNav();
