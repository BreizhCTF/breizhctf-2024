<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

use App\Models\User;

class RegisterController extends Controller
{
    public function process(Request $request)
    {
        $params = request()->all();
        if(isset($params["pseudo"]) && isset($params["email"]) && isset($params["password"]) &&
           !empty($params["pseudo"]) && !empty($params["email"]) && !empty($params["password"]))
        {
            if(strlen($params["pseudo"]) < 255 && strlen($params["email"]) && filter_var($params["email"], FILTER_VALIDATE_EMAIL))
            {
                if(empty(User::where('email', $params["email"])->first()))
                {
                    $user = new User();
                    $user->name = $params["pseudo"];
                    $user->email = $params["email"];
                    $user->password = $params["password"];
                    $user->save();
                    $request->session()->put("ok","Votre compte a bien été créé.");
                }
                else
                {
                    $request->session()->put("error","L'email est déjà utilisé.");
                    $request->session()->put("modal","registerModal");
                }
            }
            else
            {
                $request->session()->put("error","Des paramètres sont incorrects.");
                $request->session()->put("modal","registerModal");
            }
        }
        else
        {
            $request->session()->put("error","Il manque des paramètres.");
            $request->session()->put("modal","registerModal");
        }
        return redirect('/');
    }
}
