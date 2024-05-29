<?php

namespace App;

use Exception;

class FormParser
{
    public function __construct($name = "", $nb_fields = 0, $fields = "")
    {
        $this->error = "";
        $this->name = $name;
        $this->nb_fields = $nb_fields;
        $this->fields = [];
        $this->parse_fields($fields);
        if($this->name !== "" && sizeof($this->fields) == 0)
        {
            throw new Exception("Error while rendering form");
        }
    }

    public function handleError($form_name)
    {
        $template = file_get_contents("/app/error_log_template.txt");
        $error = str_replace("%HERE%",$form_name,$template);
        file_put_contents("/app/errors.log", $error, FILE_APPEND);
        $this->error = "Une erreur est survenue lors de la création de votre formulaire, notre équipe a été prévenue, veuillez nous en excuser.";
    }

    function parse_fields($fields)
    {
        if(strlen($fields) > 0)
        {
            $decode_fields = json_decode(base64_decode($fields), true);
            for($i=0; $i<$this->nb_fields;$i++)
            {
                array_push($this->fields, $decode_fields[$i]);
            }
        }
    }

    public static function __callStatic($method, $args)
    {
        throw new Exception('Bad method called on FormParser::'.$method);
    }

    public function __call($method, $args)
    {
        throw new Exception('Bad method called on FormParser->'.$method);
    }
}