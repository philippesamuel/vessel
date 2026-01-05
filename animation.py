from manim import *
import numpy as np
from torispherical_head import TorisphericalHead


class DrawKloepper(Scene):
    def construct(self):
        # 1. Initialize your engineering model
        head = TorisphericalHead(external_diameter=6.0) # Scaled for Manim screen
        
        # 2. Define the Arcs using your derived theta
        # Crown Arc (from 90 degrees down to 90-theta)
        crown_arc = Arc(
            radius=head.crown_radius,
            start_angle=PI/2,
            angle=-head.theta,
            arc_center=head.crown_center_y * UP
        ).set_color(BLUE)

        # Knuckle Arc (from 90-theta down to 0)
        knuckle_arc = Arc(
            radius=head.knuckle_radius,
            start_angle=PI/2 - head.theta,
            angle=-(PI/2 - head.theta),
            arc_center=head.knuckle_center_x * RIGHT + head.knuckle_center_y * UP
        ).set_color(RED)

        # 3. Create Labels and Annotations
        title = Text("Klöpperboden Geometry (DIN 28011)", font_size=36).to_edge(UP)
        theta_label = MathTex(r"\theta = \arcsin\left(\frac{4}{9}\right) \approx 26.39^\circ")
        theta_label.next_to(crown_arc.get_end(), RIGHT, buff=0.5).scale(0.8)

        # 4. Animation Sequence
        self.play(Write(title))
        self.wait(1)
        
        self.play(Create(crown_arc), run_time=2)
        self.play(Create(knuckle_arc), run_time=1.5)
        
        # Highlight transition
        dot = Dot(point=head.transition_point_x * RIGHT + head.transition_point_y * UP, color=YELLOW)
        self.play(FadeIn(dot), Write(theta_label))
        
        # Mirror the other side to show the full head
        full_head = VGroup(crown_arc, knuckle_arc, dot)
        mirrored_head = full_head.copy().stretch(-1, 0, about_point=ORIGIN)
        
        self.play(TransformFromCopy(full_head, mirrored_head))
        self.wait(2)

def main() -> None:
    animation = DrawKloepper()
    

if __name__ == "__main__":
    main()

