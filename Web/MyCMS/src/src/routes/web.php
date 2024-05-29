<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\LoginController;
use App\Http\Controllers\RegisterController;
use App\Http\Controllers\FormController;
use App\Http\Controllers\AdminController;
use App\Http\Middleware\EnsureUserIsAdmin;
use App\Http\Middleware\EnsureUserIsConnected;
use App\Http\Middleware\EnsureUserIsNotConnected;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

//Flag 1 route
Route::get('/flag1', [AdminController::class, 'flag1'])->name('flag');

//Basic routes
Route::get('/', [HomeController::class, 'index'])->name('home');

//Unauthenticate routes
Route::post('/login', [LoginController::class, 'process'])->middleware(EnsureUserIsNotConnected::class)->name('loginProcess');
Route::post('/register', [RegisterController::class, 'process'])->middleware(EnsureUserIsNotConnected::class)->name('registerProcess');


//Authenticate routes
Route::get('/form', [FormController::class, 'index'])->middleware(EnsureUserIsConnected::class)->name('form');
Route::post('/form', [FormController::class, 'process'])->middleware(EnsureUserIsConnected::class)->name('formProcess');
Route::delete('/form', [FormController::class, 'delete'])->middleware(EnsureUserIsConnected::class)->name('formDelete');
Route::get('/export', [FormController::class, 'export'])->middleware(EnsureUserIsConnected::class)->name('formExport');
Route::get('/logout', [LoginController::class, 'logout'])->middleware(EnsureUserIsConnected::class)->name('logout');

//Admin routes
Route::get('/admin', [AdminController::class, 'index'])->middleware(EnsureUserIsAdmin::class)->name('admin');
Route::get('/admin/logs/download', [AdminController::class, 'download'])->middleware(EnsureUserIsAdmin::class)->name('adminDownload');
Route::post('/admin/logs/template', [AdminController::class, 'change'])->middleware(EnsureUserIsAdmin::class)->name('adminChangeTemplate');