/*!
 * Lazy Load - JavaScript plugin for lazy loading images
 *
 * Copyright (c) 2007-2019 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 * Project home:
 *   https://appelsiini.net/projects/lazyload
 *
 * Version: 2.0.0-rc.2
 *
 */ !function(a,b){"object"==typeof exports?module.exports=b(a):"function"==typeof define&&define.amd?define([],b):a.LazyLoad=b(a)}("undefined"!=typeof global?global:this.window||this.global,function(a){"use strict";"function"==typeof define&&define.amd&&(a=window);let c={src:"data-src",srcset:"data-srcset",selector:".lazyload",root:null,rootMargin:"0px",threshold:0},d=function(){let b={},c=!1,a=0,e=arguments.length;for("[object Boolean]"===Object.prototype.toString.call(arguments[0])&&(c=arguments[0],a++);a<e;a++){let f=arguments[a];!function(e){for(let a in e)Object.prototype.hasOwnProperty.call(e,a)&&(c&&"[object Object]"===Object.prototype.toString.call(e[a])?b[a]=d(!0,b[a],e[a]):b[a]=e[a])}(f)}return b};function b(a,b){this.settings=d(c,b||{}),this.images=a||document.querySelectorAll(this.settings.selector),this.observer=null,this.init()}if(b.prototype={init:function(){if(!a.IntersectionObserver){this.loadImages();return}let c=this,b={root:this.settings.root,rootMargin:this.settings.rootMargin,threshold:[this.settings.threshold]};this.observer=new IntersectionObserver(function(a){Array.prototype.forEach.call(a,function(a){if(a.isIntersecting){c.observer.unobserve(a.target);let b=a.target.getAttribute(c.settings.src),d=a.target.getAttribute(c.settings.srcset);"img"===a.target.tagName.toLowerCase()?(b&&(a.target.src=b),d&&(a.target.srcset=d)):a.target.style.backgroundImage="url("+b+")"}})},b),Array.prototype.forEach.call(this.images,function(a){c.observer.observe(a)})},loadAndDestroy:function(){this.settings&&(this.loadImages(),this.destroy())},loadImages:function(){if(!this.settings)return;let a=this;Array.prototype.forEach.call(this.images,function(b){let c=b.getAttribute(a.settings.src),d=b.getAttribute(a.settings.srcset);"img"===b.tagName.toLowerCase()?(c&&(b.src=c),d&&(b.srcset=d)):b.style.backgroundImage="url('"+c+"')"})},destroy:function(){this.settings&&(this.observer.disconnect(),this.settings=null)}},a.lazyload=function(a,c){return new b(a,c)},a.jQuery){let $=a.jQuery;$.fn.lazyload=function(a){return(a=a||{}).attribute=a.attribute||"data-src",new b($.makeArray(this),a),this}}return b})