#!/bin/bash

echo "Crear entorno virtual para el desarrollo"
ENV=`ls | grep *env`
REQS=`ls | grep req*.txt`
DIRECTORY=`pwd`
ENV_NAME="env"

if [[ "$EUID" -eq 0 ]];then
    echo "No correr como root"
    exit
fi

if [[ -n "$ENV" ]]; then
    echo "Ya existe el entorno virtual en $ENV"
else
    read -p "Creado entorno virtual en  $DIRECTORY, quieres continuar? [y/n] " opt
    case "$opt" in
        *y*|*Y*)
        opt="y" ;;
        *n*|*N*)
        opt="n" ;;
        *)
        echo "¯\_(ツ)_/¯" ;;
    esac

fi


if [[ "$opt" = "y" ]]; then

    echo "creando entorno $ENV_NAME"
   out=`python3 -m virtualenv $ENV_NAME`


elif [[ "$opt" = "n" ]]; then

    echo "cancelado"

else
    echo  "¯\_(ツ)_/¯"
fi

read -p "Quieres instalar los paquetes desde req.txt en el entorno?  [y,n] " opt
case "$opt" in
    *y*|*Y*)
    opt="y" ;;
    *n*|*N*)
    opt="n" ;;
    *)
    echo "¯\_(ツ)_/¯" ;;
esac

if [[ "$opt" = "y" && -n "$REQS" ]]; then

    echo "instalando dependencias en el entorno virtual"
    source "$ENV"/bin/activate
    file="$REQS"
    while read -r line
    do
        pip3 install "$line"
    done < $file





elif [[ "$opt" = "n" ]]; then

    echo "cancelado"

else
    echo  "¯\_(ツ)_/¯"
fi