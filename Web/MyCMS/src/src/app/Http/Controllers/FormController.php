<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Form;
use App\Models\User;
use App\FormParser;
use Mpdf\Mpdf;
use Exception;

class FormController extends Controller
{
    public function index(Request $request)
    {
        $params = request()->all();
        $target_formulaire = "example";
        if(isset($params["id"]) && !empty($params["id"]))
        {
            $target_formulaire = $params["id"];
        }
        else
        {
            return view('create_form');
        }

        if($target_formulaire !== "me")
        {
            $form = Form::select(['content', 'user_id', 'renderer', 'nb_fields', 'name'])->where("name", $target_formulaire)->first();
            if(!empty($form))
            {
                $form_user = User::select('email')->where('id',$form["user_id"])->first();
                if($form_user["email"] !== $request->session()->get('email'))
                {
                    return view('form', ['error' => 'Ce formulaire ne vous appartient pas.']);
                    exit;
                }
                else
                {
                    try{
			
                        $renderer = new $form["renderer"]($form['name'], $form['nb_fields'], $form["content"], "feur");
                    } catch(\Throwable $e) {
                        $renderer = new $form["renderer"]();
                        $renderer->handleError($form['name']);
                        return view('form', ['error' => $renderer->error]);
                    }
                    $html = '<h2 class="text-center">Formulaire: '.$target_formulaire.'</h2><div class="container text-center"><div class="row-4"><div class="form-row align-items-center">';
                    foreach($renderer->fields as $field)
                    {
                        $html .= '<div class="col-sm-3 my-1"><label for="'.$field["name"].'">'.$field["type"].' :</label>';
                        switch($field["type"]) {
                            case "email":
                                $html .= "<input type='email' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='worty@breizhctf.fr'>";
                                break;
                            case "password":
                                $html .= "<input type='password' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='**********'>";
                                break;
                            case "text":
                                $html .= "<input type='text' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='Random text'>";
                                break;
                            default:
                                $html .= "<input type='text' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='Random text'>";
                                break;
                        }
                        $html .= "</div>";
                    }
                    $html .= "</div></div></div><div class='container mt-3'><div class='text-center'><button class='btn btn-primary' onclick='alert(\"Ce site est en version bêta, les formulaires ne peuvent pas encore être collectés.\")'>Envoyer le formulaire</button></div></div>";
                    return view('form', ['formname' => $form['name'], "html" => $html]);
                }
            }
            else
            {
                return view('form', ['error' => 'Le formulaire spécifié n\'existe pas.']);
                exit;
            }
        }
        else
        {
            $current_user = User::select('id')->where('email',$request->session()->get('email'))->first();
            $all_forms = Form::select(['name'])->where('user_id',$current_user["id"])->get();
            if(sizeof($all_forms) == 0)
            {
                return view('form', ['error' => 'Vous n\'avez pas encore créé de formulaire.']);
                exit;
            }
            else
            {
                $names = [];
                foreach($all_forms as $form)
                {
                    array_push($names, $form["name"]);
                }
                return view('form', ['me' => 1, 'names' => $names]);
                exit;
            }
        }
    }

    public function process(Request $request)
    {
        $params = request()->all();
        header("Content-Type: application/json");
        if(isset($params["nb_fields"]) && isset($params["content"]) && isset($params["name"])
            && !empty($params["content"]) && !empty($params["name"]))
        {
            if(!empty(Form::where("name", $params["name"])->first()))
            {
                echo '{"error":"Ce nom de formulaire est déjà pris, veuillez en choisir un autre."}';
                exit;
            }

            if((stripos($params["name"], '"') !== false) || (stripos($params["name"], "'") !== false)
                || (stripos($params["name"], "<") !== false) || (stripos($params["name"], ">") !== false))
            {
                echo '{"error":"Les données reçues sont incorrectes."}';
                exit;
            }

            $content = json_decode(base64_decode($params["content"]), true);
            if(sizeof($content) != $params["nb_fields"])
            {
                echo '{"error":"Le nombre de champ ne correspond pas aux données reçues."}';
                exit;
            }

            //Verify the data
            foreach($content as $field)
            {
                if(sizeof($field) != 3)
                {
                    echo '{"error":"Les données reçues sont incorrectes."}';
                    exit;
                }
                if(isset($field["name"]) && isset($field["type"]) && isset($field["size"])
                    && !empty($field["name"]) && !empty($field["type"]) && !empty($field["size"]))
                {
                    if(((strlen($field["name"]) > 50) || (strlen($field["name"]) < 2)) || preg_match('/[^a-z_\-0-9]/i', $field["name"]))
                    {
                        echo '{"error":"Les données reçues sont incorrectes."}';
                        exit;
                    }
                    if((stripos($field["name"], '"') !== false) || (stripos($field["name"], "'") !== false)
                        || (stripos($field["name"], "<") !== false) || (stripos($field["name"], ">") !== false))
                    {
                        echo '{"error":"Les données reçues sont incorrectes."}';
                        exit;
                    }
                    if(!in_array($field["type"], ["email","text","password"]))
                    {
                        echo '{"error":"Les données reçues sont incorrectes."}';
                        exit;
                    }
                    if((intval($field["size"]) > 50) || (intval($field["size"]) < 5))
                    {
                        echo '{"error":"Les données reçues sont incorrectes."}';
                        exit;
                    }
                }
                else
                {
                    echo '{"error":"Les données reçues sont incorrectes."}';
                    exit;
                }
            }

            //Data are verified else the script would have exit
            $current_user = User::select("id")->where("email", $request->session()->get('email'))->first();
            $to_insert = array_merge(request()->except('_token'), ["user_id" => $current_user["id"]]);
            Form::create($to_insert);
            echo '{"ok":"Le formulaire a bien été créé !"}';
        }
        else
        {
            echo '{"error":"Il manque des paramètres."}';
            exit;
        }
    }

    public function delete(Request $request)
    {
        header("Content-Type: application/json");
        $params = request()->all();
        if(isset($params["name"]) && !empty($params["name"]))
        {
            $form = Form::select(['user_id'])->where("name", $params["name"])->first();
            if(!empty($form))
            {
                $form_user = User::select('email')->where('id',$form["user_id"])->first();
                if($form_user["email"] !== $request->session()->get('email'))
                {
                    echo '{"error":"Ce formulaire ne vous appartient pas."}';
                    exit;
                }
                else
                {
                    Form::where('name', $params["name"])->delete();
                    echo '{"ok":"Le formulaire a bien été supprimé."}';
                }
            }
            else
            {
                echo '{"error":"Le formulaire spécifié n\'existe pas."}';
                exit;
            }
        }
        else
        {
            echo '{"error":"Il manque des paramètres."}';
            exit;
        }
    }

    public function export(Request $request)
    {
        $params = request()->all();
        if(isset($params["name"]) && !empty($params["name"]))
        {
            $form = Form::select(['user_id', 'name', 'content', 'renderer', 'nb_fields'])->where("name", $params["name"])->first();
            if(!empty($form))
            {
                $form_user = User::select('email')->where('id',$form["user_id"])->first();
                if($form_user["email"] !== $request->session()->get('email'))
                {
                    return view('form', ['error' => 'Ce formulaire ne vous appartient pas.']);
                    exit;
                }
                else
                {
                    try{
                        $renderer = new $form["renderer"]($form['name'], $form['nb_fields'], $form["content"]);
                    } catch(\Throwable $e) {
                        $renderer = new $form["renderer"]();
                        $renderer->handleError($form['name']);
                        return view('form', ['error' => $renderer->error]);
                    }
                    $html = '<h2 class="text-center">Formulaire: '.$form['name'].'</h2><div class="container text-center"><div class="row-4"><div class="form-row align-items-center">';
                    foreach($renderer->fields as $field)
                    {
                        $html .= '<div class="col-sm-3 my-1"><label for="'.$field["name"].'">'.$field["type"].' :</label>';
                        switch($field["type"]) {
                            case "email":
                                $html .= "<input type='email' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='worty@breizhctf.fr'>";
                                break;
                            case "password":
                                $html .= "<input type='password' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='**********'>";
                                break;
                            case "text":
                                $html .= "<input type='text' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='Random text'>";
                                break;
                            default:
                                $html .= "<input type='text' name='".$field["name"]."' id='".$field["name"]."' max='".$field["size"]."' placeholder='Random text'>";
                                break;
                        }
                        $html .= "</div>";
                    }
                    $html .= "</div></div></div><div class='container mt-3'><div class='text-center'><button class='btn btn-primary' onclick='alert(\"Ce site est en version bêta, les formulaires ne peuvent pas encore être collectés.\")'>Envoyer le formulaire</button></div></div>";
                    $mpdf = new Mpdf();
                    $mpdf->writeHTML($html);
                    $mpdf->Output();
                    exit;
                }
            }
            else
            {
                return view('form', ['error' => 'Le formulaire spécifié n\'existe pas.']);
                exit;
            }
        }
        else
        {
            return view('form', ['error' => 'Il manque des paramètres.']);
            exit;
        }
    }
}
