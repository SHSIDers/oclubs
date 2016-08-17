var gulp = require('gulp');
var compass = require('gulp-compass');
var autoprefixer = require('gulp-autoprefixer');


var input = './oclubs/static/sass/*.scss';
var output = './oclubs/static/css';
var style = 'compressed';

var compassOptions = {
	sass: './oclubs/static/sass',
	css: './oclubs/static/css',
	logging: true,
	comments: false,
	style: style
};

var sassOptions = {
	errLogToConsole: true,
	outputStyle: style,
	lineComments: false,
};

var autoprefixerOptions = {
	browsers: [
		'last 2 versions',
		'> 5%',
		'Firefox ESR',

		// https://github.com/twbs/bootstrap-sass#sass-autoprefixer
		'Android 2.3',
		'Android >= 4',
		'Chrome >= 20',
		'Firefox >= 24',
		'Explorer >= 8',
		'iOS >= 6',
		'Opera >= 12',
		'Safari >= 6'
	]
};

gulp.task('sass', function () {
	return gulp
		.src(input)
		.pipe(compass(compassOptions))
		.pipe(autoprefixer(autoprefixerOptions))
		.pipe(gulp.dest(output));
});

gulp.task('watch', function() {
	return gulp
		.watch(input, ['sass'])
		.on('change', function(event) {
			console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
		});
});

gulp.task('default', ['sass', 'watch']);
