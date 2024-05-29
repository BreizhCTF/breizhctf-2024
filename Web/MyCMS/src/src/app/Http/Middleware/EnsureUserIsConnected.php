<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use App\CustomSessionHandler;

class EnsureUserIsConnected
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if(CustomSessionHandler::is_session_param_defined('email', $request)) 
        {
            return $next($request);
        }
        else
        {
            return redirect('/');
        }
        
    }
}
