#include <asf.h>
#include "conf_board.h"

#include "gfx_mono_ug_2832hsweg04.h"
#include "gfx_mono_text.h"
#include "sysfont.h"


//clk
#define clk_PIO     PIOC
#define clk_PIO_ID  ID_PIOC
#define clk_PIO_PIN 19
#define clk_PIO_PIN_MASK (1 << clk_PIO_PIN)
//dt
#define dt_PIO     PIOA
#define dt_PIO_ID  ID_PIOA
#define dt_PIO_PIN 6
#define dt_PIO_PIN_MASK (1 << dt_PIO_PIN)
//sw
#define sw_PIO     PIOD
#define sw_PIO_ID  ID_PIOD
#define sw_PIO_PIN 30
#define sw_PIO_PIN_MASK (1 << sw_PIO_PIN)

/** RTOS  */
#define TASK_OLED_STACK_SIZE                (1024*6/sizeof(portSTACK_TYPE))
#define TASK_OLED_STACK_PRIORITY            (tskIDLE_PRIORITY)

extern void vApplicationStackOverflowHook(xTaskHandle *pxTask,  signed char *pcTaskName);
extern void vApplicationIdleHook(void);
extern void vApplicationTickHook(void);
extern void vApplicationMallocFailedHook(void);
extern void xPortSysTickHandler(void);

/** prototypes */
QueueHandle_t xQueueValor;
void but_callback(void);

void clk_callback(void);
void dt_callback(void);
void sw_callback(void);

static void BUT_init(void);

/************************************************************************/
/* RTOS application funcs                                               */
/************************************************************************/

extern void vApplicationStackOverflowHook(xTaskHandle *pxTask, signed char *pcTaskName) {
	printf("stack overflow %x %s\r\n", pxTask, (portCHAR *)pcTaskName);
	for (;;) {	}
}

extern void vApplicationIdleHook(void) { }

extern void vApplicationTickHook(void) { }

extern void vApplicationMallocFailedHook(void) {
	configASSERT( ( volatile void * ) NULL );
}

/************************************************************************/
/* handlers / callbacks                                                 */
/************************************************************************/

void but_callback(void) {
}

//sentido horario - clk cai antes
void clk_callback(void){
	if(pio_get(dt_PIO,PIO_INPUT,dt_PIO_PIN_MASK)){
		int valor = 1;
  		BaseType_t xHigherPriorityTaskWoken = pdTRUE;
  		xQueueSendFromISR(xQueueValor, &valor, &xHigherPriorityTaskWoken);
	};
};

//sentido anti horario - dt cai antes
void dt_callback(void){
	if(pio_get(sw_PIO,PIO_INPUT,sw_PIO_PIN_MASK)){
		int valor = -1;
  		BaseType_t xHigherPriorityTaskWoken = pdTRUE;
  		xQueueSendFromISR(xQueueValor, &valor, &xHigherPriorityTaskWoken);
	};
};
void sw_callback(void){
	
};
/************************************************************************/
/* TASKS                                                                */
/************************************************************************/

static void task_oled(void *pvParameters) {
	gfx_mono_ssd1306_init();
  	gfx_mono_draw_string("Testando", 0, 0, &sysfont);
  	char string_soma[3];
  
  
	int valor;
	int soma = 0;
	for (;;)  {
		
		if(xQueueReceive(xQueueValor,&(valor),(TickType_t) 0)){
			soma = soma+valor;
			sprintf(string_soma,"%d",soma);
			gfx_mono_draw_string(string_soma, 0, 20, &sysfont);
		}
	}
}

/************************************************************************/
/* funcoes                                                              */
/************************************************************************/

static void configure_console(void) {
	const usart_serial_options_t uart_serial_options = {
		.baudrate = CONF_UART_BAUDRATE,
		.charlength = CONF_UART_CHAR_LENGTH,
		.paritytype = CONF_UART_PARITY,
		.stopbits = CONF_UART_STOP_BITS,
	};

	/* Configure console UART. */
	stdio_serial_init(CONF_UART, &uart_serial_options);

	/* Specify that stdout should not be buffered. */
	setbuf(stdout, NULL);
}

static void BUT_init(void) {

	pmc_enable_periph_clk(clk_PIO_ID);
  	pmc_enable_periph_clk(dt_PIO_ID);
  	pmc_enable_periph_clk(sw_PIO_ID);
	/* configura prioridae */

	//CONFIGS PARA CLK
	pio_configure(clk_PIO, PIO_INPUT, clk_PIO_PIN_MASK, PIO_DEBOUNCE);
	pio_set_debounce_filter(clk_PIO, clk_PIO_PIN_MASK, 60);
	pio_handler_set(clk_PIO, clk_PIO_ID, clk_PIO_PIN_MASK, PIO_IT_FALL_EDGE , clk_callback);
	pio_enable_interrupt(clk_PIO, clk_PIO_PIN_MASK);
	pio_get_interrupt_status(clk_PIO);

	NVIC_EnableIRQ(clk_PIO_ID);
	NVIC_SetPriority(clk_PIO_ID, 4);

	//CONFIGS PARA dt
	pio_configure(dt_PIO, PIO_INPUT, dt_PIO_PIN_MASK, PIO_DEBOUNCE);
	pio_set_debounce_filter(dt_PIO, dt_PIO_PIN_MASK, 60);
	pio_handler_set(dt_PIO, dt_PIO_ID, dt_PIO_PIN_MASK, PIO_IT_FALL_EDGE , dt_callback);
	pio_enable_interrupt(dt_PIO, dt_PIO_PIN_MASK);
	pio_get_interrupt_status(dt_PIO);

	NVIC_EnableIRQ(dt_PIO_ID);
	NVIC_SetPriority(dt_PIO_ID, 4);


	//CONFIGS PARA sw
	pio_configure(sw_PIO, PIO_INPUT, sw_PIO_PIN_MASK, PIO_DEBOUNCE);
	pio_set_debounce_filter(sw_PIO, sw_PIO_PIN_MASK, 60);
	pio_handler_set(sw_PIO, sw_PIO_ID, sw_PIO_PIN_MASK, PIO_IT_FALL_EDGE , sw_callback);
	pio_enable_interrupt(sw_PIO, sw_PIO_PIN_MASK);
	pio_get_interrupt_status(sw_PIO);

	NVIC_EnableIRQ(sw_PIO_ID);
	NVIC_SetPriority(sw_PIO_ID, 4);

}

/************************************************************************/
/* main                                                                 */
/************************************************************************/


int main(void) {
	/* Initialize the SAM system */
	sysclk_init();
	board_init();
	BUT_init();
	xQueueValor = xQueueCreate(100, sizeof(int));
	if (xQueueValor == NULL)
		printf("falha em criar a queue xQueueValor \n");
	/* Initialize the console uart */
	configure_console();

	/* Create task to control oled */
	if (xTaskCreate(task_oled, "oled", TASK_OLED_STACK_SIZE, NULL, TASK_OLED_STACK_PRIORITY, NULL) != pdPASS) {
	  printf("Failed to create oled task\r\n");
	}

	/* Start the scheduler. */
	vTaskStartScheduler();

  /* RTOS n�o deve chegar aqui !! */
	while(1){}

	/* Will only get here if there was insufficient memory to create the idle task. */
	return 0;
}
