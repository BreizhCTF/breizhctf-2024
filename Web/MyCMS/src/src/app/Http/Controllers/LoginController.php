<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;

class LoginController extends Controller
{
    public function process(Request $request)
    {
        $params = request()->all();
        if(isset($params["email"]) && isset($params["password"]) &&
           !empty($params["email"]) && !empty($params["password"]))
        {
            $user = User::select('password')->where('email', $params["email"])->first();
            $hasher = app('hash');
            if(!empty($user))
            {
                if($hasher->check($params["password"], $user->password))
                {
                    $request->session()->put("email",$params["email"]);
                    $request->session()->put("ok","Connexion réussie.");
                }
                else
                {
                    $request->session()->put("error","L'email ou le mot de passe est incorrect.");
                    $request->session()->put("modal","loginModal");
                }
            }
            else
            {
                $request->session()->put("error","L'email ou le mot de passe est incorrect.");
                $request->session()->put("modal","loginModal");
            }
        }
        else
        {
            $request->session()->put("error","Il manque des paramètres.");
            $request->session()->put("modal","loginModal");
        }
        return redirect('/');
    }

    public function logout(Request $request)
    {
        if($request->session()->has('email'))
        {
            $request->session()->forget('email');
        }
        return redirect('/');
    }
}
