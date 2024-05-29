<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Flag;

class AdminController extends Controller
{
    public function index()
    {
        return view('admin');
    }

    public function flag1()
    {
        if($_SERVER["REMOTE_ADDR"] === "127.0.0.1" && $_SERVER["REQUEST_METHOD"] === "GET")
        {
            $flag = Flag::find(1);
            $flag->display = 1;
            $flag->save();
            return redirect('/');
        }
        else
        {
            return redirect('/');
        }
    }

    public function download(Request $request)
    {
        $allowed = ["/templates/errors.log","/templates/error_log_template.txt"];
        $file = '/templates/errors.log';
        $params = request()->all();
        if(isset($params["file"]) && in_array($params["file"], $allowed))
        {
            $file = $params["file"];
        }
        if (file_exists($file)) {
            header('Content-Description: File Transfer');
            header('Content-Type: application/octet-stream');
            header('Content-Disposition: attachment; filename="' . basename($file) . '"');
            header('Expires: 0');
            header('Cache-Control: must-revalidate');
            header('Pragma: public');
            header('Content-Length: ' . filesize($file));
            readfile($file);
            exit;
        } else {
            echo "Le fichier n'existe pas.";
            exit;
        }
    }

    public function change(Request $request)
    {
        $params = request()->all();
        if(isset($params["template"]) && isset($params["file"]))
        {
            if(file_exists("/templates/".$params["file"]) && is_writable("/templates/".$params["file"]))
            {
                if(strlen($params["template"]) <= 50)
                {
                    if(!file_put_contents($params["file"], $params["template"], LOCK_EX))
                    {
                        $request->session()->put("error","Erreur lors de la modification du fichier de template.");
                    }
                    else
                    {
                        $request->session()->put("ok","Le fichier de template a bien été modifié.");
                    }
                }
                else
                {
                    $request->session()->put("error","Le contenu du fichier de template ne doit pas dépasser 100 caractères.");
                }
            }
            else
            {
                $request->session()->put("error","Le fichier de template spécifié n'existe pas ou sa modification est interdite.");
            }
        }
        else
        {
            $request->session()->put("error","Il manque des paramètres.");
        }
        return redirect('/admin');
    }
}
