<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Form extends Model
{
    use HasFactory;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',
        'content',
        'user_id',
        'renderer',
        'nb_fields'
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'id' => 'integer',
        'name' => 'string',
        'content' => 'string',
        'user_id' => 'integer',
        'renderer' => 'string',
        'nb_fields' => 'integer'
    ];

    public $timestamps = false;

    protected $table = "form";
}
