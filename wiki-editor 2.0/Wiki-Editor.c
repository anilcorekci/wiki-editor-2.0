#include <stdio.h>
#include <stdlib.h>

char command[100];

int main( int argc, char *argv[] )  {
    if( argc >= 2 ) {
	/*	for (int i = 0; i < argc; i++) {
		    sprintf(command,"./wiki-editor '%s' &", argv[i]); 
		}*/
		sprintf(command,"./wiki-editor '%s' ", argv[1]); 
		system(command);
    }
    else {
        system("./wiki-editor");
    }

}
