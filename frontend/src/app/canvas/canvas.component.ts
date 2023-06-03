import {AfterViewInit, Component, ElementRef, ViewChild} from '@angular/core';
import {finalize, fromEvent, switchMap, takeUntil, tap} from "rxjs";
import {HttpClient} from "@angular/common/http";

@Component({
  selector: 'app-canvas',
  templateUrl: './canvas.component.html',
  styleUrls: ['./canvas.component.scss']
})
export class CanvasComponent implements AfterViewInit{

  @ViewChild('canvas', {static: true}) canvas: ElementRef<HTMLCanvasElement>;
  ctx: CanvasRenderingContext2D | null;
  isBackgroundFilled = false;
  text: string = '';

  constructor(private http: HttpClient) {}

  ngAfterViewInit() {
    this.ctx = this.canvas.nativeElement.getContext('2d');
    const mouseDownStream = fromEvent(this.canvas.nativeElement, 'mousedown');
    const mouseMoveStream = fromEvent(this.canvas.nativeElement, 'mousemove');
    const mouseUpStream = fromEvent(window, 'mouseup');

    mouseDownStream.pipe(
      tap((event: Event) => {
        if (this.ctx) {
          const rect = this.canvas.nativeElement.getBoundingClientRect();

          const offsetX = (event as MouseEvent).clientX - rect.left;
          const offsetY = (event as MouseEvent).clientY - rect.top;

          if (!this.isBackgroundFilled) {
            this.ctx.fillStyle = 'white';
            this.ctx.fillRect(0, 0, rect.width, rect.height);
            this.isBackgroundFilled = true;
          }

          this.ctx.beginPath();
          this.ctx.strokeStyle = 'black';
          this.ctx.lineWidth = 5;
          this.ctx.lineJoin = 'round';
          this.ctx.moveTo(offsetX, offsetY);
        }
      }),
      switchMap(() => mouseMoveStream.pipe(
        tap((event: Event) => {
          if (this.ctx) {
            const rect = this.canvas.nativeElement.getBoundingClientRect();
            const offsetX = (event as MouseEvent).clientX - rect.left;
            const offsetY = (event as MouseEvent).clientY - rect.top;

            this.ctx.lineTo(offsetX, offsetY);
            this.ctx.stroke();
          }
        }),
        takeUntil(mouseUpStream),
        finalize(() => {
          if (this.ctx) {
            this.ctx.closePath();
          }
        })
      ))
    ).subscribe();
  }


  clean() {
    if (this.ctx) {
      const rect = this.canvas.nativeElement.getBoundingClientRect();
      this.ctx.fillStyle = 'white';
      this.ctx.fillRect(0, 0, rect.width, rect.height);
    }
  }

  saveCanvasAsImage() {
    const canvas = this.canvas.nativeElement;
    const dataURL = canvas.toDataURL('image/png');
    this.http.post('http://127.0.0.1:5000/read_handwriting', {image: dataURL}).subscribe(
    (response:any) => {
      this.text = response['text']
    })
  }
}
