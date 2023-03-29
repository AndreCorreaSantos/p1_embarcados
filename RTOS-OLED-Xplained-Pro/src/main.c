#include <asf.h>
#include "conf_board.h"

#include "gfx_mono_ug_2832hsweg04.h"
#include "gfx_mono_text.h"
#include "sysfont.h"


#define LED_1_PIO PIOA
#define LED_1_PIO_ID ID_PIOA
#define LED_1_IDX 0
#define LED_1_IDX_MASK (1 << LED_1_IDX)

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

#define TASK_OLED_STACK_SIZE                (1024*6/sizeof(portSTACK_TYPE))
#define TASK_OLED_STACK_PRIORITY            (tskIDLE_PRIORITY)

extern void vApplicationStackOverflowHook(xTaskHandle *pxTask,  signed char *pcTaskName);
extern void vApplicationIdleHook(void);
extern void vApplicationTickHook(void);
extern void vApplicationMallocFailedHook(void);
extern void xPortSysTickHandler(void);

/** prototypes */
QueueHandle_t xQueueValor;
QueueHandle_t xQueueTempo;
QueueHandle_t xQueueCaractere;

volatile int dt_flag;
volatile int clk_flag;

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
	// clk_flag = 1;
	if(pio_get(dt_PIO,PIO_INPUT,dt_PIO_PIN_MASK)){ // && 
		int valor = 1;
  		BaseType_t xHigherPriorityTaskWoken = pdTRUE;
  		xQueueSendFromISR(xQueueValor, &valor, &xHigherPriorityTaskWoken);
	}else{
		int valor = -1;
  		BaseType_t xHigherPriorityTaskWoken = pdTRUE;
  		xQueueSendFromISR(xQueueValor, &valor, &xHigherPriorityTaskWoken);
	};
};

//sentido anti horario - dt cai antes
// void dt_callback(void){
// 	dt_flag = 1;
// 	if(!clk_flag){ //pio_get(sw_PIO,PIO_INPUT,sw_PIO_PIN_MASK) && 
// 		int valor = -1;
//   		BaseType_t xHigherPriorityTaskWoken = pdTRUE;
//   		xQueueSendFromISR(xQueueValor, &valor, &xHigherPriorityTaskWoken);
// 	};
// };
void sw_callback(void){
	BaseType_t xHigherPriorityTaskWoken = pdTRUE;

	if(pio_get(sw_PIO,PIO_INPUT,sw_PIO_PIN_MASK)){
		int contagem = rtt_read_timer_value(RTT);
		if(contagem > 5*32768){
			int v = 1;
			xQueueSendFromISR(xQueueTempo,&v,&xHigherPriorityTaskWoken); //manda um valor para fila de tempo para piscar led e zerar valores da lista
		}
	}
	if(!pio_get(sw_PIO,PIO_INPUT,sw_PIO_PIN_MASK)){
		rtt_init(RTT,1);
		int n_carac = 1;
  		xQueueSendFromISR(xQueueCaractere, &n_carac, &xHigherPriorityTaskWoken);
	}


};
/************************************************************************/
/* TASKS                                                                */
/************************************************************************/


static void task_oled(void *pvParameters) {
	gfx_mono_ssd1306_init();
  	char string_soma[10] = "0x0000";
	char string_index[10];
  
  
	int valor;
	int n_carac;
	int contador = 0;
	int soma[4] = {0,0,0,0};
	int index = 0;
	int v;
	for (;;)  {
		if(xQueueReceive(xQueueValor,&(valor),(TickType_t) 0)){
			soma[index] = soma[index]+valor;
			soma[index] = soma[index] % 15;
			if(soma[index] < 0){
				soma[index] = 15;
			}
			sprintf(string_soma,"0x%x%x%x%x ",soma[0],soma[1],soma[2],soma[3]);
		}
		if(xQueueReceive(xQueueCaractere,&(n_carac),(TickType_t) 0)){
			index += n_carac;
			index = index % 4;
			sprintf(string_index,"index: %d ",index);
			gfx_mono_draw_string(string_index, 50, 25, &sysfont);
		}
		if(xQueueReceive(xQueueTempo,&(v),(TickType_t) 0)){
			//zera index, zera array e pisca led
			index = 0;
			soma[0] = 0;
			soma[1] = 0;
			soma[2] = 0;
			soma[3] = 0;
			int i = 0;
			sprintf(string_soma,"0x%x%x%x%x ",soma[0],soma[1],soma[2],soma[3]);
			sprintf(string_index,"index: %d ",index);
			while(i<10){
				pio_clear(LED_1_PIO, LED_1_IDX_MASK);
				vTaskDelay(200);
				pio_set(LED_1_PIO, LED_1_IDX_MASK);
				vTaskDelay(200);
				i++;
			}
			gfx_mono_draw_string(string_soma, 0, 10, &sysfont);

			//pisca led
		}
		gfx_mono_draw_string(string_soma, 0, 10, &sysfont);
		//piscando
		if(contador > 5){
			//chamar task pisca
			gfx_mono_draw_string(' ',(index+2)*6,10,&sysfont);
		}
		contador++;
		contador = contador % 10;
		vTaskDelay(50);
		
		
	}
}

// static void task_pisca(void *pvParameters) {
// 	gfx_mono_ssd1306_init();
// 	int contador = 0;
// 	int index = 0;
// 	int n_carac;
// 	for (;;)  {
// 		if(xQueueReceive(xQueueCaractere,&(n_carac),(TickType_t) 0)){
// 			index += n_carac;
// 			index = index % 4;
// 		}
// 		//piscando
// 		if(contador > 5){
// 			gfx_mono_draw_string(' ',(index+2)*6,10,&sysfont);
// 		}
// 		contador++;
// 		contador = contador % 10;
// 		vTaskDelay(50);
		
		
// 	}
// }



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
	pmc_enable_periph_clk(LED_1_PIO_ID);
	pio_configure(LED_1_PIO, PIO_OUTPUT_1, LED_1_IDX_MASK, PIO_DEFAULT);

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
	// pio_handler_set(dt_PIO, dt_PIO_ID, dt_PIO_PIN_MASK, PIO_IT_FALL_EDGE , dt_callback);
	// pio_enable_interrupt(dt_PIO, dt_PIO_PIN_MASK);
	// pio_get_interrupt_status(dt_PIO);

	// NVIC_EnableIRQ(dt_PIO_ID);
	// NVIC_SetPriority(dt_PIO_ID, 4);


	//CONFIGS PARA sw
	pio_configure(sw_PIO, PIO_INPUT, sw_PIO_PIN_MASK, PIO_DEBOUNCE);
	pio_set_debounce_filter(sw_PIO, sw_PIO_PIN_MASK, 60);
	pio_handler_set(sw_PIO, sw_PIO_ID, sw_PIO_PIN_MASK, PIO_IT_EDGE , sw_callback);
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

	xQueueCaractere = xQueueCreate(100, sizeof(int));
	if (xQueueCaractere == NULL)
		printf("falha em criar a queue xQueueCaractere \n");\

	xQueueTempo = xQueueCreate(100, sizeof(int));
	if (xQueueTempo == NULL)
		printf("falha em criar a queue xQueueTempo \n");
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
